from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import mlflow

default_args = {
    'owner': 'mlops',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def register_model():
    mlflow.set_tracking_uri("http://host.docker.internal:5000")
    result = mlflow.register_model(
        model_uri="file:///app/models/best_model.pkl",
        name="DeliveryTimePrediction"
    )
    print(f">>> Registered version: {result.version}")

with DAG(
    dag_id='daily_dvc_retrain',
    default_args=default_args,
    description='Run DVC pipeline + push + register daily',
    schedule_interval='0 0 * * *',  # ทุกเที่ยงคืน
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=['retrain', 'dvc', 'mlflow']
) as dag:

    run_dvc_repro = BashOperator(
        task_id='dvc_repro',
        bash_command='cd /app && dvc repro',
    )

    run_dvc_push = BashOperator(
        task_id='dvc_push',
        bash_command='cd /app && dvc push',
    )

    register_mlflow_model = PythonOperator(
        task_id='register_model',
        python_callable=register_model,
    )

    run_dvc_repro >> run_dvc_push >> register_mlflow_model
