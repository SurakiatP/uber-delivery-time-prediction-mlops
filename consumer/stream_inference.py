import json
import time
import requests
from kafka import KafkaConsumer
import os

# Kafka consumer config
consumer = KafkaConsumer(
    'orders',
    bootstrap_servers='kafka:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='stream_inference_group'
)

# FastAPI prediction endpoint
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "fastapi_app")
FASTAPI_PORT = os.getenv("FASTAPI_PORT", "8000")
FASTAPI_URL = f"http://{FASTAPI_HOST}:{FASTAPI_PORT}/predict"

print("[*] Stream inference is running...")

for message in consumer:
    order_data = message.value
    print(f"[v] Received Order: {order_data}")

    try:
        # Call FastAPI /predict
        response = requests.post(FASTAPI_URL, json=order_data)
        if response.status_code == 200:
            prediction = response.json()
            print(f">>> Predicted Delivery Time: {prediction['predicted_delivery_time_minutes']} minutes\n")
        else:
            print(f"[!] Prediction failed: Status Code {response.status_code}, Response: {response.text}\n")

    except Exception as e:
        print(f"[!] Error during inference: {str(e)}")

    time.sleep(1)  # optional: control stream speed
