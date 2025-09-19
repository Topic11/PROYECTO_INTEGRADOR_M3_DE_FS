#!/bin/bash
# Este script se asegura de que las dependencias de dbt (dbt_utils) se instalen
# antes de ejecutar cualquier otro comando.
set -e

echo ">>> entrypoint.sh: Instalando dependencias de dbt (dbt_utils)..."
# Corre 'dbt deps' dentro de la carpeta del proyecto dbt
dbt deps --project-dir ./youtube_dbt_project

# Ahora, ejecuta el comando principal que se le pasó al contenedor
# (en nuestro caso, será `python youtubepipeline_e2e.py`)
echo ">>> entrypoint.sh: Iniciando script principal de Python..."
exec "$@"
