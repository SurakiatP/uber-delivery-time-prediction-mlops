from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import mlflow
import os

default_args = {
    'owner': 'mlops',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def register_model():
    try:
        os.chdir("/app")
        mlflow.set_tracking_uri("http://host.docker.internal:5000")
        experiment_name = "DeliveryTimePrediction"
        experiment = mlflow.get_experiment_by_name(experiment_name)

        if experiment is None:
            raise ValueError(f"Experiment '{experiment_name}' not found.")

        print(f"[MLflow] Experiment ID: {experiment.experiment_id}")

        runs = mlflow.search_runs(
            experiment_ids=[experiment.experiment_id],
            order_by=["start_time DESC"],
            max_results=5
        )

        if runs.empty:
            print("[MLflow] No runs found in experiment. Try inspecting manually:")
            print(f"→ http://host.docker.internal:5000/#/experiments/{experiment.experiment_id}")
            raise ValueError("No MLflow runs found to register.")

        latest_run = runs.iloc[0]
        run_id = latest_run.run_id
        print(f"[MLflow] Latest run ID: {run_id}")
        model_uri = f"runs:/{run_id}/model"

        result = mlflow.register_model(
            model_uri=model_uri,
            name="DeliveryTimePrediction"
        )
        print(f"[MLflow] Registered new version: {result.version}")

    except Exception as e:
        print(f"[ERROR] Failed to register model: {e}")
        raise

with DAG(
    dag_id='daily_dvc_retrain',
    default_args=default_args,
    description='Run DVC pipeline + register daily',
    schedule_interval='0 0 * * *',
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=['retrain', 'dvc', 'mlflow']
) as dag:

    run_dvc_pull = BashOperator(
        task_id='dvc_pull',
        bash_command='cd /app && dvc pull',
        do_xcom_push=False
    )

    run_dvc_repro = BashOperator(
        task_id='dvc_repro',
        bash_command='cd /app && dvc repro',
        do_xcom_push=False
    )

    register_mlflow_model = PythonOperator(
        task_id='register_model',
        python_callable=register_model
    )

    # Workflow: pull -> repro -> register
    run_dvc_pull >> run_dvc_repro >> register_mlflow_model
