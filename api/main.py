import os
import onnxruntime as rt
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import threading

app = FastAPI(title="California Housing Inference Service")

MODEL_PATH = "/app/models/model.onnx"
sess = None
lock = threading.Lock()

def load_model():
    global sess
    with lock:
        if sess is not None:
            return True
        try:
            if os.path.exists(MODEL_PATH):
                print(f"🔄 Loading model from: {MODEL_PATH}")
                sess = rt.InferenceSession(MODEL_PATH)
                print("✅ Model loaded successfully!")
                return True
            else:
                print(f"⚠️ Model file not found at {MODEL_PATH}")
                return False
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False

@app.on_event("startup")
def startup_event():
    load_model()

@app.get("/health")
def health():
    is_loaded = load_model()
    if is_loaded and sess is not None:
        return {"status": "ok"}
    return {"status": "degraded", "reason": "model_not_found"}

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
    if sess is None:
        if not load_model():
            raise HTTPException(status_code=503, detail="Model not loaded")
    
    input_data = np.array([[
        data.MedInc, data.HouseAge, data.AveRooms, data.AveBedrms,
        data.Population, data.AveOccup, data.Latitude, data.Longitude
    ]], dtype=np.float32)

    input_name = sess.get_inputs()[0].name
    label_name = sess.get_outputs()[0].name
    prediction = sess.run([label_name], {input_name: input_data})[0]
    return {"median_house_value": float(prediction[0])}
