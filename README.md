# Uber Delivery Time Prediction with MLOps
> LinkedIn Post => https://www.linkedin.com/posts/surakiat-kansa-ard-171942351_machinelearning-mlops-dataengineering-activity-7325073161790627840-SlB3?utm_source=share&utm_medium=member_desktop&rcm=ACoAAFfhzmUB4WlIO47UV21HFYwE3cHBLvtpy4A

This repository provides an end-to-end MLOps solution for predicting Uber delivery times, combining advanced data engineering, real-time inference, automated retraining, and monitoring using cutting-edge tools and best practices in the industry.

## Overview
The Uber Delivery Time Prediction system leverages machine learning and streaming data to predict delivery durations in real-time. It integrates MLOps practices, containerization, CI/CD workflows, automated retraining pipelines, and extensive monitoring and logging capabilities.

## Project Workflow

![alt text](images_readme/Project_Structure.png)

Key components include:

- Kafka: Generates and consumes real-time order data.
- FastAPI: Serves real-time predictions and model metrics.
- MLflow: Tracks experiments, manages model registry and deployment.
- Airflow: Automates daily model retraining and registration.
- DVC: Handles data versioning, ensures reproducibility.
- PostgreSQL: Stores Airflow DAG metadata, task states, execution logs.
- Prometheus + Grafana: Provides real-time analytics, performance monitoring, and visualization.

## Docker Container Stack
The entire project runs smoothly within a Docker environment to ensure reproducibility and consistency across development, staging, and production environments.

![alt text](images_readme/Docker-Ports.png)

## Project Structure

```bash
uber-delivery-time-prediction-mlops/
│
├── docker-compose.yml                 # Docker orchestration (FastAPI, Kafka, MLflow, etc.)
│
├── fastapi_app/                       # FastAPI API for serving model predictions
│   ├── Dockerfile
│   ├── requirements-fastapi.txt
│   └── app.py
│
├── producer/                          # Kafka Producer generating mock orders
│   ├── Dockerfile
│   └── kafka_producer.py
│
├── consumer/                          # Kafka Consumer for streaming inference
│   ├── Dockerfile
│   └── stream_inference.py
│
├── mlflow_server/                     # MLflow tracking server
│   └── mlruns/                        # Volume-mounted for persistence
│
├── monitoring/                        # Monitoring stack (Prometheus + Grafana)
│   ├── prometheus/
│   │   └── prometheus.yml
│   └── grafana/
│       └── provisioning/
│           ├── datasources/
│           └── dashboards/
│
├── airflow/                           # Airflow automation for daily retraining
│   ├── dags/
│   │   └── airflow_dvc_dag.py
│   └── Dockerfile
│
├── data/                              # Project datasets (versioned via DVC)
│   ├── raw/
│   │   └── uberdrives.csv
│   └── processed/
│       ├── cleaned_uberdrives.csv
│       ├── cleaned_uberdrives_with_coords.csv
│       ├── uber_with_weather.csv
│       ├── uber_with_weather_traffic.csv
│       └── model_ready_dataset.csv
│
├── src/                               # Core pipeline logic & scripts
│   ├── data_pipeline/
│   │   ├── fetch_orders.py
│   │   ├── fetch_lat_lon.py
│   │   ├── fetch_weather.py
│   │   └── fetch_traffic.py
│   ├── preprocessing/
│   │   └── feature_engineering.py
│   ├── modeling/
│   │   └── train_model.py
│   └── monitoring/
│       ├── prometheus_metrics.py
│       └── grafana_dashboard.json
│
├── notebooks/                         # Exploratory Data Analysis
│   └── data_exploration.ipynb
│
├── .config/                           # Configuration files & secrets
│   ├── secrets.yaml
│   ├── gdrive_sa.json
│   ├── params.yaml
│   └── secrets.yaml.template
│
├── .env
├── dvc.lock
├── dvc.yaml                           # DVC Pipeline configuration
├── requirements.txt                   # Global Python dependencies
├── README.md
└── .gitignore
```

# Getting Started

## Clone Repository
```bash
git clone https://github.com/SurakiatP/uber-delivery-time-prediction-mlops.git
cd uber-delivery-time-prediction-mlops
```
## Configuration Setup (Secrets & Environment)
Before starting the project, ensure you have properly configured the following essential files with correct values:

1. `.env` File
Create a .env file at the project's root directory containing environment variables as shown below:

```bash
# Example .env configuration

# AIRFLOW CONFIG
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__CORE__FERNET_KEY= "your FERNET_KEY"
AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION=False
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow

# LOGGING FIX: Disable remote logging
AIRFLOW__LOGGING__REMOTE_LOGGING=False

# SECURITY FIX: Secret Key for all airflow services
AIRFLOW__WEBSERVER__SECRET_KEY=THIS_IS_A_SECRET_KEY_FOR_ALL_COMPONENTS

```

2. `config/secrets.yaml` File
This file stores sensitive information, such as API keys or credentials. Create the file at .config/secrets.yaml:

```bash
# Example secrets.yaml
weather_api_key: "YOUR_WEATHER_API_KEY"
traffic_api_key: "YOUR_TRAFFIC_API_KEY"
```
- Enter your relevant API keys for third-party services here.

>⚠️ Important:
Do NOT commit this file to your Git repository. It's already added to .gitignore.

>You can refer to .config/secrets.yaml.template for guidance.

3. `.config/gdrive_sa.json` File

This file contains your Google Drive Service Account credentials (JSON), enabling DVC to connect to remote storage.

Steps to create this file:

- Create a Google Cloud Service Account.
- Download the Service Account credentials JSON file.
- Save the downloaded file as .config/gdrive_sa.json.
- Sample JSON structure (example only):

```bash
{
  "type": "service_account",
  "project_id": "your_project_id",
  "private_key_id": "your_private_key_id",
  "private_key": "your_private_key",
  "client_email": "your_client_email",
  "client_id": "your_client_id"
}
```
>⚠️ Important:
Do NOT commit this file to your Git repository. It's already added to .gitignore.


## Docker Compose Setup
```bash
docker-compose up -d
```
Services will be accessible on their respective ports:

- FastAPI: http://localhost:8000
- Airflow: http://localhost:8080
- MLflow: http://localhost:5000
- Grafana: http://localhost:3000
- Prometheus: http://localhost:9090

## Running Experiments & Retraining
- Manual Retraining: Triggered via Airflow UI (daily_dvc_retrain DAG).
- Experiment Tracking: Monitor experiments through MLflow UI.

## Monitoring & Observability
Real-time model metrics and predictions are monitored using Prometheus and visualized via Grafana dashboards.

## Technologies
- Kafka for streaming data.
- FastAPI for model deployment.
- MLflow for experiment tracking and model registry.
- Apache Airflow for pipeline orchestration.
- DVC for data versioning.
- Docker for containerization.
- Prometheus & Grafana for monitoring and analytics.
- PostgreSQL as Airflow's backend database.

# Contribution
Contributions are welcome! Please open issues or submit pull requests.

---

## Project Author

| Name           | Contact Information                                                  |
|----------------|----------------------------------------------------------------------|
| **Surakiat P.** |                                                                      |
| 📧 Email       | [surakiat.0723@gmail.com](mailto:surakiat.0723@gmail.com)   |
| 🔗 LinkedIn    | [linkedin.com/in/surakiat](https://www.linkedin.com/in/surakiat-kansa-ard-171942351/)     |
| 🌐 GitHub      | [github.com/SurakiatP](https://github.com/SurakiatP)                 |
