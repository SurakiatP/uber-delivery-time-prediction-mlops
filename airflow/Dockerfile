FROM apache/airflow:2.8.1-python3.10

USER root

RUN apt-get update && apt-get install -y git libpq-dev gcc

USER airflow

WORKDIR /app

RUN pip install --no-cache-dir dvc[gdrive] psycopg2-binary mlflow xgboost lightgbm
