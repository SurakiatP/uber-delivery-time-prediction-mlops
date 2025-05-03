import pandas as pd
import os

RAW_PATH = "data/raw/uberdrives.csv"
PROCESSED_PATH = "data/processed/cleaned_uberdrives.csv"

def load_and_clean_orders():
    # Load raw data
    df = pd.read_csv(RAW_PATH)

    # Clean column names
    df.columns = df.columns.str.replace('*', '', regex=False)

    # Drop rows with missing critical fields
    df = df.dropna(subset=['END_DATE', 'CATEGORY', 'START', 'STOP'])

    # Convert datetime
    df['START_DATE'] = pd.to_datetime(df['START_DATE'])
    df['END_DATE'] = pd.to_datetime(df['END_DATE'])

    # Calculate trip duration in minutes
    df['TRIP_DURATION_MINUTES'] = (df['END_DATE'] - df['START_DATE']).dt.total_seconds() / 60

    # Filter out invalid durations
    df = df[(df['TRIP_DURATION_MINUTES'] > 0) & (df['TRIP_DURATION_MINUTES'] < 300)]

    # Save cleaned data
    os.makedirs(os.path.dirname(PROCESSED_PATH), exist_ok=True)
    df.to_csv(PROCESSED_PATH, index=False)
    print(f"[+] Cleaned orders saved to {PROCESSED_PATH}")

if __name__ == "__main__":
    load_and_clean_orders()
