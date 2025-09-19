# Versión final - Forzando reconstrucción
FROM python:3.11-slim
ENV PIP_NO_CACHE_DIR=1 PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /root/.dbt
COPY .dbt/profiles.yml /root/.dbt/profiles.yml
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "youtubepipeline_e2e.py"]
