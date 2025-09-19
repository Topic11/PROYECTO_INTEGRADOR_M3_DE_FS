#!/usr/bin/env python3
import os, json, csv, io, datetime, subprocess
from google.cloud import storage, bigquery
import requests

API_BASE = "https://www.googleapis.com/youtube/v3"
DBT_PROJECT_DIR = "youtube_dbt_project"

def _run_dbt_command(command_list):
    full_command = ["dbt"] + command_list
    print(f">>> Ejecutando: {' '.join(full_command)}")
    # Usamos cwd para correr dbt desde adentro de su carpeta de proyecto
    result = subprocess.run(full_command, cwd=DBT_PROJECT_DIR, capture_output=True, text=True, check=False)
    print(result.stdout)
    if result.returncode != 0:
        print("--- ERROR EN DBT ---")
        print(result.stderr)
        # Hacemos que el script falle si dbt falla
        raise RuntimeError(f"dbt command '{' '.join(command_list)}' failed.")

def fetch_data(api_key, region):
    print(">>> Extrayendo datos de YouTube API...")
    cats_data = requests.get(f"{API_BASE}/videoCategories", params={"part":"snippet","regionCode":region,"key":api_key}).json()
    vids_data = requests.get(f"{API_BASE}/videos", params={"part":"snippet,statistics","chart":"mostPopular","regionCode":region,"maxResults":50,"key":api_key}).json()
    return cats_data, vids_data

def process_data(cats_data, vids_data):
    categories = [{"category_id": int(it['id']), "category_name": it['snippet']['title']} for it in cats_data.get("items", [])]
    videos = []
    for it in vids_data.get("items", []):
        sn, st = it.get('snippet', {}), it.get('statistics', {})
        videos.append({
            "video_id": it.get("id"), "title": sn.get("title"), "channel_title": sn.get("channelTitle"),
            "publish_time": sn.get("publishedAt"),
            "category_id": int(sn.get("categoryId")) if sn.get("categoryId") else None,
            "view_count": int(st.get("viewCount")) if st.get("viewCount") else None,
            "like_count": int(st.get("likeCount")) if st.get("likeCount") else None,
            "comment_count": int(st.get("commentCount")) if st.get("commentCount") else None
        })
    return categories, videos

def upload_to_gcs(bucket, path, data, content_type):
    client = storage.Client()
    blob = client.bucket(bucket).blob(path)
    blob.upload_from_string(data, content_type=content_type)
    print(f"▲ gs://{bucket}/{path}")

def load_to_bq(project, gcs_uri, table_id, config):
    client = bigquery.Client(project=project)
    job = client.load_table_from_uri(gcs_uri, f"{project}.raw.{table_id}", job_config=config)
    job.result()
    print(f"✔ raw.{table_id}")

def main():
    PROJECT = os.environ["PROJECT"]
    BUCKET  = os.environ["BUCKET"]
    APIKEY  = os.environ["YT_API_KEY"]
    DATE    = datetime.datetime.utcnow().date().isoformat()
    PREFIX  = f"raw/youtube/US/date={DATE}/"

    cats_data, vids_data = fetch_data(APIKEY, "US")
    categories, videos = process_data(cats_data, vids_data)

    print(">>> Subiendo archivos a GCS...")
    cols = videos[0].keys()
    buf = io.StringIO(); w = csv.DictWriter(buf, fieldnames=cols); w.writeheader(); w.writerows(videos)
    upload_to_gcs(BUCKET, f"{PREFIX}youtube_mostpopular.csv", buf.getvalue(), "text/csv")
    
    ndjson_bytes = "\n".join(json.dumps(r) for r in categories)
    upload_to_gcs(BUCKET, f"{PREFIX}youtube_categories.ndjson", ndjson_bytes, "application/x-ndjson")

    print(">>> Cargando datos a BigQuery RAW...")
    load_to_bq(PROJECT, f"gs://{BUCKET}/{PREFIX}youtube_mostpopular.csv", "youtube_mostpopular", bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.CSV, autodetect=True, write_disposition="WRITE_TRUNCATE"))
    load_to_bq(PROJECT, f"gs://{BUCKET}/{PREFIX}youtube_categories.ndjson", "youtube_categories", bigquery.LoadJobConfig(source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON, autodetect=True, write_disposition="WRITE_TRUNCATE"))

    print(">>> Ejecutando transformaciones dbt...")
    _run_dbt_command(["seed", "--full-refresh"])
    _run_dbt_command(["run"])
    _run_dbt_command(["test"])
    print("OK ✅ E2E listo")

if __name__ == "__main__":
    main()
