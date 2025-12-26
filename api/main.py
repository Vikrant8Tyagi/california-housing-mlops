import os
import mlflow.onnx
import onnxruntime as rt
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="CalHousings Inference Service")

# 1. Load the model from MLflow Registry
# We use the 'latest' version of 'California_Housing_Model'
MODEL_NAME = "California_Housing_Model"
mlflow.set_tracking_uri(os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000"))

print("Fetching model from MLflow...")
model_uri = f"models:/{MODEL_NAME}/latest"
model_onnx = mlflow.onnx.load_model(model_uri)
sess = rt.InferenceSession(model_onnx.SerializeToString())

# 2. Define Input Schema (Based on PDF Page 8)
class HousingData(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict")
def predict(data: HousingData):
    # Convert input to numpy array
    input_data = np.array([[
        data.MedInc, data.HouseAge, data.AveRooms, data.AveBedrms,
        data.Population, data.AveOccup, data.Latitude, data.Longitude
    ]], dtype=np.float32)
    
    # Run Inference
    input_name = sess.get_inputs()[0].name
    label_name = sess.get_outputs()[0].name
    prediction = sess.run([label_name], {input_name: input_data})[0]
    
    return {"median_house_value": float(prediction[0])}
