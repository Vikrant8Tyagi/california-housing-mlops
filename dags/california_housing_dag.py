from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# This ensures Airflow can find the 'training' folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'training')))

# Import the new functions we just wrote in train.py
from train import train_model, validate_data 

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'california_housing_dag',
    default_args=default_args,
    description='Phase 1: Automated Training Pipeline for CalHousings Inc.',
    schedule_interval='@daily',  # Project Requirement: Runs daily
    catchup=False,
) as dag:

    # Task 1: Data Validation (Includes fetching if missing)
    data_validation = PythonOperator(
        task_id="data_validation",
        python_callable=validate_data,
    )

    # Task 2: Model Training (Random Forest + ONNX + Registration)
    model_training = PythonOperator(
        task_id="model_training",
        python_callable=train_model,
    )

    # Dependency: Validation must pass before Training
    data_validation >> model_training
