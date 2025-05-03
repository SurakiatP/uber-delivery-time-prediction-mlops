from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pandas as pd
import mlflow
import os
import time

from src.monitoring.prometheus_metrics import (
    prometheus_middleware,
    metrics as prometheus_metrics,
    PREDICTION_SUCCESS_COUNT,
    PREDICTION_FAILURE_COUNT,
    PREDICTION_LATENCY,
    PREDICTION_DISTANCE
)

# FastAPI Application Setup
app = FastAPI(
    title="Delivery Time Prediction API",
    description="Predicts estimated delivery time (minutes) from order features.",
    version="1.3"
)

# Register Prometheus Middleware
app.middleware("http")(prometheus_middleware)

# Set MLflow Tracking URI
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://host.docker.internal:5000"))

# Load ML Model
MODEL_URI = os.getenv("MODEL_URI", "models:/DeliveryTimePrediction/Production")
model = None
load_error = None

try:
    model = mlflow.pyfunc.load_model(MODEL_URI)
except Exception as e:
    load_error = str(e)

# Expected Input Columns
expected_columns = [
    'DISTANCE_KM', 'HOUR', 'DAY_OF_WEEK', 'IS_WEEKEND', 'IS_NIGHT',
    'WEATHER_SEVERITY', 'TRAFFIC_SEVERITY',
    'temperature', 'humidity', 'wind_speed',
    'DISTANCE_BIN_2to5km', 'DISTANCE_BIN_5to10km', 'DISTANCE_BIN_less_2km', 'DISTANCE_BIN_more_10km',
    'HOUR_BUCKET_Afternoon', 'HOUR_BUCKET_Evening', 'HOUR_BUCKET_Morning', 'HOUR_BUCKET_Night',
    'TRAFFIC_High', 'TRAFFIC_Low', 'TRAFFIC_Medium',
    'WEATHER_Clear', 'WEATHER_Clouds', 'WEATHER_Haze', 'WEATHER_Rain'
]

# Pydantic Input Schema
class DeliveryInput(BaseModel):
    DISTANCE_KM: float
    HOUR: int
    DAY_OF_WEEK: int
    IS_WEEKEND: int
    IS_NIGHT: int
    WEATHER_SEVERITY: float
    TRAFFIC_SEVERITY: float
    temperature: float
    humidity: float
    wind_speed: float
    WEATHER_Clear: int = 0
    WEATHER_Clouds: int = 0
    WEATHER_Haze: int = 0
    WEATHER_Rain: int = 0
    TRAFFIC_High: int = 0
    TRAFFIC_Low: int = 0
    TRAFFIC_Medium: int = 0
    HOUR_BUCKET_Morning: int = 0
    HOUR_BUCKET_Afternoon: int = 0
    HOUR_BUCKET_Evening: int = 0
    HOUR_BUCKET_Night: int = 0
    DISTANCE_BIN_less_2km: int = 0
    DISTANCE_BIN_2to5km: int = 0
    DISTANCE_BIN_5to10km: int = 0
    DISTANCE_BIN_more_10km: int = 0

# Prediction Endpoint
@app.post("/predict", tags=["Prediction"])
async def predict_delivery_time(features: DeliveryInput):
    if model is None:
        PREDICTION_FAILURE_COUNT.inc()
        raise HTTPException(status_code=503, detail=f"Model not loaded: {load_error}")

    try:
        input_df = pd.DataFrame([features.dict()])

        # Ensure all expected columns exist
        for col in expected_columns:
            if col not in input_df.columns:
                input_df[col] = 0

        input_df = input_df[expected_columns]

        # Track prediction latency
        start_time = time.time()
        prediction = model.predict(input_df)
        latency = time.time() - start_time
        PREDICTION_LATENCY.observe(latency)

        # Update other metrics
        PREDICTION_DISTANCE.observe(features.DISTANCE_KM)
        PREDICTION_SUCCESS_COUNT.inc()

        predicted_minutes = float(prediction[0])

        return {"predicted_delivery_time_minutes": round(predicted_minutes, 2)}

    except Exception as e:
        PREDICTION_FAILURE_COUNT.inc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

# Health Check Endpoint
@app.get("/", tags=["Health Check"])
async def read_root():
    if model is None:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "message": f"Model not loaded: {load_error}"}
        )
    return {"status": "ok", "message": "Delivery Time Prediction API is alive!"}

# Prometheus Metrics Endpoint
@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    return Response(prometheus_metrics(), media_type="text/plain")
