from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


def sanity_check():
    print("✅ California Housing Step 2 DAG is working")


with DAG(
    dag_id="california_housing_step2",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["california", "mlops", "step2"]
) as dag:

    sanity_task = PythonOperator(
        task_id="sanity_check",
        python_callable=sanity_check
    )

    sanity_task
