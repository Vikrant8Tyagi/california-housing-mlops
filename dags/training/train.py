import os
import pandas as pd
import numpy as np
import mlflow
import mlflow.sklearn
import mlflow.onnx
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.datasets import fetch_california_housing
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Shared volume path inside Docker
DATA_PATH = "/opt/airflow/data/housing.csv"

def validate_data():
    """Phase 1: Data Validation Requirement"""
    if not os.path.exists(DATA_PATH):
        print("Dataset not found. Fetching from sklearn...")
        data = fetch_california_housing(as_frame=True)
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        data.frame.to_csv(DATA_PATH, index=False)
    
    df = pd.read_csv(DATA_PATH)
    
    # Check for nulls (Project Requirement)
    if df.isnull().values.any():
        raise ValueError("Validation Failed: Null values found in dataset")
    
    # Check for expected columns
    if len(df.columns) < 9:
        raise ValueError(f"Validation Failed: Expected 9 columns, found {len(df.columns)}")
            
    print("✅ Data Validation Passed")

def train_model():
    """Phase 1: Random Forest Training & ONNX Registration"""
    # 1️⃣ Setup MLflow
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("california-housing")

    # 2️⃣ Load Data
    df = pd.read_csv(DATA_PATH)
    # The sklearn fetcher uses 'MedHouseVal' as the target name
    target_col = 'MedHouseVal' if 'MedHouseVal' in df.columns else 'target'
    X = df.drop(target_col, axis=1)
    y = df[target_col]

    # 3️⃣ Training (Requirement: Random Forest)
    params = {
        "n_estimators": 100,
        "max_depth": 10,
        "random_state": 42
    }

    with mlflow.start_run():
        model = RandomForestRegressor(**params)
        model.fit(X, y)

        # 4️⃣ Metrics (Requirement: MSE and R2)
        predictions = model.predict(X)
        mse = mean_squared_error(y, predictions)
        r2 = r2_score(y, predictions)

        mlflow.log_params(params)
        mlflow.log_metric("mse", mse)
        mlflow.log_metric("r2", r2)
        
        # Log the standard sklearn model
        mlflow.sklearn.log_model(model, "sklearn_model")

        # 5️⃣ ONNX Conversion (Requirement for Phase 2 API)
        initial_type = [('float_input', FloatTensorType([None, X.shape[1]]))]
        onx = convert_sklearn(model, initial_types=initial_type)
        
        # Log ONNX artifact and Register Model in Registry
        mlflow.onnx.log_model(
            onx, 
            "model_onnx", 
            registered_model_name="California_Housing_Model"
        )
        
        print(f"✅ Success! MSE: {mse:.4f}, R2: {r2:.4f}")
        print("✅ Model registered as 'California_Housing_Model' in MLflow.")

if __name__ == "__main__":
    train_model()
