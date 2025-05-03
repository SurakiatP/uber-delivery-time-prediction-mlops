import requests
import pandas as pd
import time
import yaml
import os

def load_api_key():
    with open("config/secrets.yaml", "r") as f:
        secrets = yaml.safe_load(f)
    return secrets['openweathermap']['api_key']

API_KEY = load_api_key()
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

def fetch_weather(lat, lon):
    url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temperature": data['main']['temp'],
            "humidity": data['main']['humidity'],
            "weather": data['weather'][0]['main'],
            "wind_speed": data['wind']['speed'],
        }
    else:
        print(f"[!] Failed to fetch weather for lat={lat}, lon={lon}")
        return {
            "temperature": None,
            "humidity": None,
            "weather": None,
            "wind_speed": None
        }

def enrich_with_weather(input_path, output_path):
    df = pd.read_csv(input_path)
    weather_records = []

    for index, row in df.iterrows():
        lat, lon = row['LAT'], row['LON']
        weather = fetch_weather(lat, lon)
        weather_records.append(weather)
        time.sleep(1)

    weather_df = pd.DataFrame(weather_records)
    enriched_df = pd.concat([df.reset_index(drop=True), weather_df], axis=1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    enriched_df.to_csv(output_path, index=False)
    print(f"[+] Weather-enriched data saved to {output_path}")

if __name__ == "__main__":
    INPUT_PATH = "data/processed/cleaned_uberdrives_with_coords.csv"
    OUTPUT_PATH = "data/processed/uber_with_weather.csv"
    enrich_with_weather(INPUT_PATH, OUTPUT_PATH)
