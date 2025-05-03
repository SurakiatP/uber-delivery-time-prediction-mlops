import pandas as pd
import numpy as np
import os

def simulate_traffic_conditions(input_path, output_path):
    df = pd.read_csv(input_path)
    
    traffic_levels = ['Low', 'Medium', 'High']
    probabilities = [0.5, 0.3, 0.2]
    np.random.seed(42)

    df['TRAFFIC_CONDITION'] = np.random.choice(traffic_levels, size=len(df), p=probabilities)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[+] Traffic data added and saved to {output_path}")

if __name__ == "__main__":
    INPUT_PATH = "data/processed/uber_with_weather.csv"
    OUTPUT_PATH = "data/processed/uber_with_weather_traffic.csv"
    simulate_traffic_conditions(INPUT_PATH, OUTPUT_PATH)
