import pandas as pd
import requests
import time
import os

def fetch_lat_lon(address):
    """
    Use Nominatim (OpenStreetMap) to fetch latitude and longitude for a given address.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/search?q={address}&format=json"
        headers = {"User-Agent": "Mozilla/5.0 (compatible; DeliveryTimeML/1.0)"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            return float(data['lat']), float(data['lon'])
        else:
            return None, None
    except Exception as e:
        print(f"[!] Error fetching location for {address}: {e}")
        return None, None

def add_lat_lon_to_orders(input_path, output_path):
    """
    Load cleaned orders, add lat/lon columns based on START location, and save processed file.
    """
    df = pd.read_csv(input_path)

    latitudes = []
    longitudes = []

    for idx, row in df.iterrows():
        address = row['START']
        lat, lon = fetch_lat_lon(address)
        latitudes.append(lat)
        longitudes.append(lon)

        time.sleep(1)

    df['LAT'] = latitudes
    df['LON'] = longitudes

    # Delete rows that cannot find lat/lon.
    df = df.dropna(subset=['LAT', 'LON'])

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[+] Saved file with coordinates to {output_path}")

if __name__ == "__main__":
    INPUT_PATH = "data/processed/cleaned_uberdrives.csv"
    OUTPUT_PATH = "data/processed/cleaned_uberdrives_with_coords.csv"
    add_lat_lon_to_orders(INPUT_PATH, OUTPUT_PATH)
