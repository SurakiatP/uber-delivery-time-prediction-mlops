# src/preprocessing/feature_engineering.py

import pandas as pd
import numpy as np
import os

def clean_and_convert_features(df: pd.DataFrame) -> pd.DataFrame:
    # Remove duplicate columns
    df = df.loc[:, ~df.columns.duplicated()]

    # Convert boolean columns to int (True/False → 1/0)
    bool_cols = df.select_dtypes(include=["bool"]).columns
    df[bool_cols] = df[bool_cols].astype(int)

    return df

def feature_engineering(input_path, output_path):
    """
    Feature Engineering Pipeline:
    - Select important columns
    - Generate distance, time, weather, traffic features
    - One-hot encode categorical features
    - Clean booleans & duplicates
    - Save model-ready CSV
    """
    df = pd.read_csv(input_path)

    # Step 1: Select relevant columns
    df = df[[ 
        'START_DATE', 'MILES', 'TRIP_DURATION_MINUTES', 
        'temperature', 'humidity', 'wind_speed', 
        'weather', 'TRAFFIC_CONDITION'
    ]]

    # Step 2: Distance Features
    df['DISTANCE_KM'] = df['MILES'] * 1.60934
    df['DISTANCE_BIN'] = pd.cut(
        df['DISTANCE_KM'],
        bins=[0, 2, 5, 10, np.inf],
        labels=['less_2km', '2to5km', '5to10km', 'more_10km']
    )

    # Step 3: Time Features
    df['START_DATE'] = pd.to_datetime(df['START_DATE'])
    df['HOUR'] = df['START_DATE'].dt.hour
    df['DAY_OF_WEEK'] = df['START_DATE'].dt.dayofweek
    df['IS_WEEKEND'] = df['DAY_OF_WEEK'].apply(lambda x: 1 if x >= 5 else 0)
    df['IS_NIGHT'] = df['HOUR'].apply(lambda x: 1 if (x <= 5 or x >= 22) else 0)

    def bucket_hour(hour):
        if 5 <= hour < 11:
            return 'Morning'
        elif 11 <= hour < 17:
            return 'Afternoon'
        elif 17 <= hour < 22:
            return 'Evening'
        else:
            return 'Night'
    df['HOUR_BUCKET'] = df['HOUR'].apply(bucket_hour)

    # Step 4: Severity Mapping
    weather_severity = {
        'Clear': 0, 'Clouds': 1, 'Mist': 1, 'Haze': 1,
        'Rain': 2, 'Drizzle': 2, 'Thunderstorm': 3, 'Snow': 3
    }
    df['WEATHER_SEVERITY'] = df['weather'].map(weather_severity).fillna(1)

    traffic_severity = {
        'Low': 0, 'Medium': 1, 'High': 2
    }
    df['TRAFFIC_SEVERITY'] = df['TRAFFIC_CONDITION'].map(traffic_severity).fillna(1)

    # Step 5: One-hot encoding
    weather_ohe = pd.get_dummies(df['weather'], prefix='WEATHER')
    traffic_ohe = pd.get_dummies(df['TRAFFIC_CONDITION'], prefix='TRAFFIC')
    hour_bucket_ohe = pd.get_dummies(df['HOUR_BUCKET'], prefix='HOUR_BUCKET')
    distance_bin_ohe = pd.get_dummies(df['DISTANCE_BIN'], prefix='DISTANCE_BIN')

    # Combine all
    df = pd.concat([df, weather_ohe, traffic_ohe, hour_bucket_ohe, distance_bin_ohe], axis=1)

    # Step 6: Drop unused columns
    df = df.drop(columns=[
        'MILES', 'START_DATE', 'weather', 'TRAFFIC_CONDITION',
        'HOUR_BUCKET', 'DISTANCE_BIN'
    ])

    # Step 7: Reorder columns
    base_columns = [
        'DISTANCE_KM', 'HOUR', 'DAY_OF_WEEK', 'IS_WEEKEND', 'IS_NIGHT',
        'WEATHER_SEVERITY', 'TRAFFIC_SEVERITY',
        'temperature', 'humidity', 'wind_speed'
    ]
    ohe_columns = sorted([
        col for col in df.columns
        if col.startswith('WEATHER_') or col.startswith('TRAFFIC_') 
        or col.startswith('HOUR_BUCKET_') or col.startswith('DISTANCE_BIN_')
    ])
    target_column = 'TRIP_DURATION_MINUTES'
    final_columns = base_columns + ohe_columns + [target_column]

    df = df[final_columns]

    # Step 7.5: Clean boolean types & duplicates
    df = clean_and_convert_features(df)

    # Step 8: Save output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[+] Feature-engineered dataset saved to {output_path}")

if __name__ == "__main__":
    INPUT_PATH = "data/processed/uber_with_weather_traffic.csv"
    OUTPUT_PATH = "data/processed/model_ready_dataset.csv"
    feature_engineering(INPUT_PATH, OUTPUT_PATH)
