from prometheus_client import Counter, Histogram, generate_latest
import time
from starlette.requests import Request
from starlette.responses import Response

# Metrics Definitions
REQUEST_COUNT = Counter("request_count_total", "Total HTTP requests", ["method", "endpoint"])
REQUEST_LATENCY = Histogram("request_latency_seconds", "HTTP request latency", ["method", "endpoint"])
PREDICTION_SUCCESS_COUNT = Counter("prediction_success_count", "Number of successful predictions")
PREDICTION_FAILURE_COUNT = Counter("prediction_failure_count", "Number of failed predictions")
PREDICTION_LATENCY = Histogram("prediction_latency_seconds", "Prediction latency in seconds")
PREDICTION_DISTANCE = Histogram("prediction_input_distance_km", "Distance input to prediction model", buckets=[0, 2, 5, 10, 20, float("inf")])

# Middleware Function with 2 args
async def prometheus_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path

    start_time = time.time()
    try:
        response = await call_next(request)
        return response
    finally:
        elapsed = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(elapsed)

# Expose metrics for /metrics endpoint
def metrics():
    return generate_latest()
