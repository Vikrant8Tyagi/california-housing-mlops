from sklearn.datasets import fetch_california_housing
import pandas as pd
import os

def fetch_data():
    data = fetch_california_housing(as_frame=True)
    df = data.frame

    data_dir = "/opt/airflow/data"
    os.makedirs(data_dir, exist_ok=True)

    path = f"{data_dir}/california.csv"
    df.to_csv(path, index=False)

    return path
