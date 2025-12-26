import os
import pandas as pd
import mlflow
import mlflow.sklearn
import mlflow.onnx
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.datasets import fetch_california_housing
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# Path must match the volume mapping in docker-compose: ./models -> /opt/airflow/models
DATA_PATH = "/opt/airflow/data/housing.csv"
SHARED_MODEL_PATH = "/opt/airflow/models/model.onnx"

def validate_data():
    if not os.path.exists(DATA_PATH):
        print("Dataset not found. Fetching from sklearn...")
        data = fetch_california_housing(as_frame=True)
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        data.frame.to_csv(DATA_PATH, index=False)
    df = pd.read_csv(DATA_PATH)
    if df.isnull().values.any():
        raise ValueError("❌ Validation Failed: Null values found")
    print("✅ Data Validation Passed")

def train_model():
    tracking_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("california-housing")

    df = pd.read_csv(DATA_PATH)
    target_col = "MedHouseVal"
    X = df.drop(target_col, axis=1)
    y = df[target_col]

    with mlflow.start_run():
        model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
        model.fit(X, y)
        
        # Log to MLflow
        mlflow.sklearn.log_model(model, "sklearn_model")
        
        # Convert and Save ONNX
        initial_type = [("float_input", FloatTensorType([None, X.shape[1]]))]
        onnx_model = convert_sklearn(model, initial_types=initial_type)
        
        mlflow.onnx.log_model(
            onnx_model, 
            "model_onnx", 
            registered_model_name="California_Housing_Model"
        )

        # Write to Shared Volume
        os.makedirs(os.path.dirname(SHARED_MODEL_PATH), exist_ok=True)
        with open(SHARED_MODEL_PATH, "wb") as f:
            f.write(onnx_model.SerializeToString())

    print(f"✅ Model saved to {SHARED_MODEL_PATH}")

if __name__ == "__main__":
    train_model()
