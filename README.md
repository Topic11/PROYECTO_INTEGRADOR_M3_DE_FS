Pipeline de Datos ELT para YouTube Trending en GCP
1. Introducción
Este proyecto implementa un pipeline de datos End-to-End (E2E) de tipo ELT (Extract - Load - Transform) para procesar datos de videos en tendencia de la API de YouTube. La solución está completamente dockerizada y desplegada en la infraestructura de Google Cloud Platform (GCP), orquestada con Apache Airflow (Cloud Composer).

El objetivo principal es extraer datos de la API, cargarlos en un Data Warehouse (BigQuery) y transformarlos en modelos de datos limpios y listos para el análisis, respondiendo a preguntas de negocio sobre tendencias, canales y categorías.

2. Arquitectura de la Solución
El pipeline sigue un flujo de datos moderno y escalable, utilizando servicios serverless de GCP para minimizar la gestión de infraestructura.

Tecnologías Utilizadas:

Fuente de Datos: YouTube Data API v3.

Contenerización: Docker.

Registro de Contenedores: Google Artifact Registry.

Computación Serverless: Google Cloud Run (Jobs) para la ejecución del pipeline.

Almacenamiento (Data Lake): Google Cloud Storage (GCS).

Data Warehouse: Google BigQuery.

Transformación de Datos: dbt (Data Build Tool).

Orquestación: Apache Airflow (Google Cloud Composer).

Gestión de Secretos: Google Secret Manager.

CI/CD: GitHub Actions.

Flujo del Pipeline:

Orquestación: Un DAG en Cloud Composer se ejecuta según un cronograma (@daily).

Ejecución: El DAG dispara un Cloud Run Job.

Extracción (Extract): El script de Python dentro del contenedor llama a la API de YouTube para obtener datos de videos populares y categorías.

Carga (Load): El script sube los datos crudos en formato CSV y NDJSON a un bucket de Google Cloud Storage. De ahí, los carga en las tablas correspondientes del dataset raw en BigQuery.

Transformación (Transform): El script invoca a dbt, que se encarga de:

Ejecutar dbt seed para cargar datos estáticos (ej: regiones).

Ejecutar dbt run para transformar los datos de la capa raw a las capas silver (staging) y gold (marts de datos).

Ejecutar dbt test para validar la calidad e integridad de los datos en los modelos finales.

3. Estructura del Proyecto
El repositorio está organizado de la siguiente manera:

proyecto-youtube-final/
│
├── .dbt/
│   └── profiles.yml             # Perfil de conexión de dbt (no subir a git público)
│
├── dags/
│   └── pi3_youtube_pipeline.py    # DAG de Airflow para orquestar el job
│
├── youtube_dbt_project/
│   ├── models/
│   │   ├── silver/              # Modelos de Staging (limpieza, casteo)
│   │   │   ├── stg_youtube_categories.sql
│   │   │   ├── stg_youtube_mostpopular.sql
│   │   │   └── schema.yml
│   │   ├── gold/                # Modelos de Data Mart (dimensiones y hechos)
│   │   │   ├── dim_category.sql
│   │   │   ├── dim_channel.sql
│   │   │   ├── dim_date.sql
│   │   │   ├── dim_video.sql
│   │   │   ├── fact_trending.sql
│   │   │   └── schema.yml
│   │   └── sources.yml            # Definición de fuentes raw
│   ├── seeds/
│   │   └── dim_region.csv         # Datos estáticos
│   ├── dbt_project.yml            # Configuración principal del proyecto dbt
│   └── packages.yml               # Dependencias de dbt (ej: dbt_utils)
│
├── .gitignore                     # Archivos y carpetas a ignorar por Git
├── Dockerfile                     # Receta para construir la imagen del pipeline
├── entrypoint.sh                  # Script de inicio del contenedor
├── requirements.txt               # Dependencias de Python
└── youtubepipeline_e2e.py         # Script principal del pipeline (Extract, Load, Trigger Transform)
4. Configuración y Despliegue
Prerrequisitos
Un proyecto de Google Cloud con la facturación habilitada.

gcloud CLI instalado y autenticado (gcloud auth login).

APIs habilitadas: Cloud Build, Artifact Registry, Cloud Run, Secret Manager, IAM, BigQuery, Cloud Composer.

Una API Key de YouTube Data API v3.

Un entorno de Cloud Composer ya desplegado.

Pasos para el Despliegue
Clonar el Repositorio:

Bash

git clone https://github.com/tu-usuario/tu-repositorio.git
cd tu-repositorio
Configurar Variables de Entorno en Cloud Shell:

Bash

export PROJECT="pi-m3-de-fs"
export REGION="us-central1"
export REPO="pi3-images"
export IMAGE="yt-pi3-e2e"
export BUCKET="pi-youtube" # Reemplazar con tu bucket de GCS
export SA="sa-pi3@$PROJECT.iam.gserviceaccount.com"
Configurar profiles.yml:
Asegurarse de que el archivo .dbt/profiles.yml apunte a tu PROJECT.

Crear el Secreto en Secret Manager:

Bash

echo -n "TU_API_KEY_DE_YOUTUBE" | gcloud secrets create YT_API_KEY --replication-policy=automatic --data-file=-
Crear Cuenta de Servicio y Asignar Permisos:

Bash

gcloud iam service-accounts create sa-pi3 --display-name "PI3 runner"
# (Seguido de los comandos gcloud add-iam-policy-binding para BigQuery, Storage y Secret Manager)
Construir y Subir la Imagen de Docker:

Bash

gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT/$REPO/$IMAGE:latest .
Crear el Cloud Run Job:

Bash

gcloud run jobs create pi3-e2e \
  --image=$REGION-docker.pkg.dev/$PROJECT/$REPO/$IMAGE:latest \
  --region=$REGION \
  --service-account=$SA \
  --max-retries=0 \
  --set-env-vars=PROJECT=$PROJECT,BUCKET=$BUCKET,REGION_CODE=US \
  --set-secrets=YT_API_KEY=YT_API_KEY:latest
5. Cómo Ejecutar el Pipeline
Ejecución Manual
Para una ejecución de prueba inmediata:

Bash

gcloud run jobs execute pi3-e2e --region=$REGION
El progreso se puede monitorear en los logs de Cloud Run.

Ejecución Orquestada
Subir el DAG a Composer:

Bash

DAGS_BUCKET=$(gcloud composer environments describe tu-composer-env --location $REGION --format='value(config.dagGcsPrefix)')
gsutil cp dags/pi3_youtube_pipeline.py "$DAGS_BUCKET/"
Gestionar desde la UI de Airflow:

Ir a la página de Cloud Composer en la consola de GCP y abrir la UI de Airflow.

El DAG youtube_daily_pipeline aparecerá en la lista.

Activar el DAG para que se ejecute según el schedule_interval (@daily) o dispararlo manualmente para una prueba.

6. Integración Continua con GitHub Actions
Para asegurar la calidad del código, se puede implementar un flujo de CI/CD simple que valide el proyecto dbt en cada push a la rama principal.

Crear un archivo en .github/workflows/ci.yml:

YAML

name: DBT CI

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  dbt-ci:
    name: "Run dbt checks"
    runs-on: ubuntu-latest

    steps:
      - name: "Checkout code"
        uses: actions/checkout@v3

      - name: "Install dbt"
        run: pip install dbt-bigquery==1.7.9

      - name: "Setup dbt profile"
        run: |
          mkdir -p ~/.dbt
          echo "${{ secrets.DBT_PROFILES_YML }}" > ~/.dbt/profiles.yml

      - name: "Install dbt dependencies"
        run: dbt deps --project-dir ./youtube_dbt_project

      - name: "Run dbt debug"
        run: dbt debug --project-dir ./youtube_dbt_project

      - name: "Build dbt models"
        run: dbt build --project-dir ./youtube_dbt_project
