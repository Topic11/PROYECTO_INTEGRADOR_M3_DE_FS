from datetime import datetime
from airflow.models.dag import DAG
from airflow.providers.google.cloud.operators.cloud_run import CloudRunExecuteJobOperator

PROJECT_ID = "pi-m3-de-fs"
REGION = "us-central1"
JOB_NAME = "pi3-e2e"

with DAG(
    dag_id="youtube_daily_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@daily",  # Se ejecutará todos los días a la medianoche UTC
    catchup=False,
    tags=["youtube", "e2e"],
) as dag:
    execute_e2e_pipeline = CloudRunExecuteJobOperator(
        task_id="trigger_cloud_run_job",
        project_id=PROJECT_ID,
        region=REGION,
        job_name=JOB_NAME,
    )
