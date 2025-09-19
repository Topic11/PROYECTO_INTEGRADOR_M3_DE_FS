# 🚀 Pipeline de Datos ELT para YouTube Trending en GCP

## 1. Resumen del Proyecto

Este proyecto implementa un pipeline de datos End-to-End (E2E) de tipo **ELT (Extract - Load - Transform)** para la ingesta y análisis de datos de videos en tendencia de YouTube. El objetivo es transformar datos crudos de una API en un Data Warehouse estructurado y validado, listo para ser consumido por analistas y responder preguntas de negocio, sentando las bases para una solución de datos robusta y escalable.

---

## 2. Arquitectura y Justificación de Herramientas 🛠️

La arquitectura fue diseñada siguiendo un enfoque **serverless** y de **bajo mantenimiento**, eligiendo cada herramienta para cumplir un rol específico y resolver los desafíos de escalabilidad y automatización planteados en las consignas.

| Componente | Herramienta Elegida | ¿Por qué se eligió esta herramienta? |
| :--- | :--- | :--- |
| **Plataforma Cloud** | **Google Cloud Platform (GCP)** | Se seleccionó por su ecosistema de servicios de datos serverless, maduros y perfectamente integrados entre sí. |
| **Contenerización** | **Docker** | **Para garantizar la portabilidad y consistencia.** Empaqueta el pipeline en una imagen autocontenida que funciona igual en cualquier entorno. |
| **Ejecución del Pipeline**| **Cloud Run Jobs** | **Para una computación serverless y costo-eficiente.** Ejecuta el contenedor solo bajo demanda, ideal para procesos batch. |
| **Data Lake** | **Google Cloud Storage (GCS)** | **Como almacenamiento de objetos desacoplado, duradero y económico.** Sirve como la zona de aterrizaje (`landing zone`) para los datos crudos. |
| **Data Warehouse** | **Google BigQuery** | **Por su escalabilidad masiva y arquitectura serverless.** Es la base perfecta para un DWH que necesita analizar grandes volúmenes de datos. |
| **Transformación** | **dbt (Data Build Tool)** | **Para aplicar las mejores prácticas de ingeniería de software a SQL.** Permite construir, testear y documentar los modelos de datos de forma modular y versionable. |
| **Orquestación** | **Cloud Composer (Airflow)**| **Para automatizar y monitorear el pipeline.** Permite definir el pipeline como código (DAGs), programar su ejecución y gestionar reintentos. |
| **CI/CD** | **GitHub y GitHub Actions**| **Para garantizar la calidad y mantenibilidad del código.** Automatiza la ejecución de tests en cada cambio, asegurando la integridad del proyecto. |

---

## 3. Estructura del Proyecto 📂

```
.
├── .dbt/
│   └── profiles.yml
├── .github/
│   └── workflows/
│       └── ci.yml
├── dags/
│   └── pi3_youtube_pipeline.py
├── docs/
│   └── PI_M3_Analysis.docx
├── youtube_dbt_project/
│   ├── models/
│   │   ├── silver/
│   │   ├── gold/
│   │   ├── sources.yml
│   │   └── schema.yml
│   ├── seeds/
│   │   └── dim_region.csv
│   └── dbt_project.yml
├── .gitignore
├── Dockerfile
├── entrypoint.sh
├── requirements.txt
└── youtubepipeline_e2e.py
```

---

## 4. Modelado de Datos y Tests 📊

El Data Warehouse está estructurado en tres capas:

* **Capa `raw` (Bronce):** Datos crudos, sin transformar.
* **Capa `silver` (Plata):** Datos limpios, casteados y estandarizados.
* **Capa `gold` (Oro):** Modelos de datos finales, listos para el consumo (dimensiones y hechos).

**NOTA**: hay un error en la toma de imagen la cual genera los schemas con un prefijo y se muestran como raw_gold y raw_silver cuando solo debiera ser gold y silver.

La **calidad de los datos** se garantiza mediante tests (`not_null`, `unique`, `relationships`) definidos en los archivos `schema.yml` de `dbt`.

---

## 5. Análisis de Datos 📈

Una vez procesados los datos y almacenados en la capa `gold`, se ejecutaron una serie de consultas SQL para responder a las preguntas de negocio clave del proyecto.

**El detalle completo de las consultas, sus resultados y las conclusiones se encuentra en el siguiente documento:**
### ➡️ **[`docs/PI_M3_Analysis.docx`](docs/PI_M3_Analysis.docx)**

---

## 6. CI/CD con GitHub Actions 🔄

Para garantizar la calidad y mantenibilidad del código, se implementó un flujo de CI/CD con GitHub Actions. El workflow, definido en `.github/workflows/ci.yml`, se dispara en cada `push` o `pull request` a la rama `main` y ejecuta los siguientes pasos:
1.  Clona el código del repositorio.
2.  Instala `dbt` y sus dependencias (como `dbt_utils`).
3.  Configura las credenciales de BigQuery de forma segura usando un secreto de GitHub.
4.  Ejecuta `dbt build`, que corre los seeds, los modelos y los tests, validando la integridad de todo el proyecto de transformación.

---

## 7. Despliegue y Ejecución

El despliegue y la ejecución se realizan mediante comandos de `gcloud` para construir la imagen de Docker, crear el Cloud Run Job y subir el DAG a Composer.

* **Ejecución Manual:**
    ```sh
    gcloud run jobs execute pi3-e2e --region=$REGION
    ```
* **Ejecución Automática:**
    El DAG `youtube_daily_pipeline` en Airflow se encarga de la ejecución programada.

---

## 8. Autor

**Federico Strologo**
