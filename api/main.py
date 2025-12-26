import os
import mlflow
import mlflow.onnx
import onnxruntime as rt
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threading

app = FastAPI(title="California Housing Inference Service")

MODEL_NAME = "California_Housing_Model"
sess = None
lock = threading.Lock()

def load_model_if_needed():
    global sess
    if sess is not None:
        return

    with lock:
        if sess is not None:
            return

        try:
            mlflow.set_tracking_uri(
                os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow:5000")
            )

            # Attempt to load from MLflow Registry
            model_uri = f"models:/{MODEL_NAME}/latest"
            model_onnx = mlflow.onnx.load_model(model_uri)
            sess = rt.InferenceSession(model_onnx.SerializeToString())
            print("✅ Model loaded successfully from MLflow")

        except Exception as e:
            print(f"❌ Model loading failed: {e}")
            sess = None

@app.on_event("startup")
def startup_event():
    """Attempt to load model on startup"""
    load_model_if_needed()

@app.get("/health")
def health():
    """Jenkins calls this. We try to load the model here if it's missing."""
    load_model_if_needed()
    if sess is None:
        return {"status": "degraded", "reason": "model not loaded"}
    return {"status": "ok"} # Jenkins looks for "ok"

class HousingData(BaseModel):
    MedInc: float
    HouseAge: float
    AveRooms: float
    AveBedrms: float
    Population: float
    AveOccup: float
    Latitude: float
    Longitude: float

@app.post("/predict")
def predict(data: HousingData):
    load_model_if_needed()
    if sess is None:
        raise HTTPException(status_code=503, detail="Model not available")

    input_data = np.array(
        [[
            data.MedInc,
            data.HouseAge,
            data.AveRooms,
            data.AveBedrms,
            data.Population,
            data.AveOccup,
            data.Latitude,
            data.Longitude,
        ]],
        dtype=np.float32,
    )

    input_name = sess.get_inputs()[0].name
    output_name = sess.get_outputs()[0].name

    prediction = sess.run([output_name], {input_name: input_data})[0]
    return {"median_house_value": float(prediction[0])}
