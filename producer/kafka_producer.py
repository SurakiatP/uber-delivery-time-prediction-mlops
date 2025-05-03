from kafka import KafkaProducer
import json
import time
import random

# Kafka Setup
producer = KafkaProducer(
    bootstrap_servers='kafka:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_valid_order():
    return {
        "DISTANCE_KM": round(random.uniform(1, 20), 2),
        "HOUR": random.randint(0, 23),
        "DAY_OF_WEEK": random.randint(0, 6),
        "IS_WEEKEND": random.choice([0, 1]),
        "IS_NIGHT": random.choice([0, 1]),
        "WEATHER_SEVERITY": random.randint(0, 3),
        "TRAFFIC_SEVERITY": random.randint(0, 2),
        "temperature": round(random.uniform(10, 35), 2),
        "humidity": random.randint(30, 100),
        "wind_speed": round(random.uniform(0, 10), 2),
        # Only include OHE fields used in model
        "DISTANCE_BIN_2to5km": random.choice([0, 1]),
        "DISTANCE_BIN_5to10km": random.choice([0, 1]),
        "DISTANCE_BIN_less_2km": random.choice([0, 1]),
        "DISTANCE_BIN_more_10km": random.choice([0, 1]),
        "HOUR_BUCKET_Afternoon": random.choice([0, 1]),
        "HOUR_BUCKET_Evening": random.choice([0, 1]),
        "HOUR_BUCKET_Morning": random.choice([0, 1]),
        "HOUR_BUCKET_Night": random.choice([0, 1]),
        "TRAFFIC_High": random.choice([0, 1]),
        "TRAFFIC_Low": random.choice([0, 1]),
        "TRAFFIC_Medium": random.choice([0, 1]),
        "WEATHER_Clear": random.choice([0, 1]),
        "WEATHER_Clouds": random.choice([0, 1]),
        "WEATHER_Haze": random.choice([0, 1]),
        "WEATHER_Rain": random.choice([0, 1])
    }

# Produce 1 order every 2 seconds
while True:
    order = generate_valid_order()
    producer.send('orders', value=order)
    print(f"[+] Produced: {order}")
    time.sleep(2)
