"""
fetch_data.py - Week 8: get data from an API and save it as a DATA/raw.csv
"""

from pathlib import Path

import pandas as pd
import requests

# Settings

URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"   

PARAMS = {
    "format": "geojson", 
    "minmagnitude": 2.5, 
    "limit": 500
}    

RECORDS_KEY = "features"     

RENAME = {
    "properties_mag": "magnitude",
    "properties_place": "location",
    "properties_time": "time",
    "properties_type": "event_type",
}

KEEP = ["magnitude", "location", "time", "type", "event_type"] 
    
MUST_HAVE = ["magnitude"]     

RAW_FILE = Path(__file__).parent / "DATA" / "raw.csv"

# Functions  
                                   
def get_data(url, params):
    try:
        response = requests.get(URL, params=PARAMS, timeout=15)
        response.raise_for_status()
        return response.json()
    
    except requests.RequestException as error:
        print("Could not get the data:", error)
        return None

def make_table(data, records_key):
    records = data[records_key] if records_key else data
    return pd.json_normalize(records, sep="_")

def tidy_data(df):
    df = df.rename(columns=RENAME)
    
    df["time"] = pd.to_datetime(
        df["time"], unit="ms"
    ).dt.strftime("%Y-%m-%d %H:%M:%S")
    
    df = df[KEEP]
    df = df.dropna(subset=MUST_HAVE)
    
    return df

def save_data(df, path):
    path.parent.mkdir(exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved {len(df)} rows to {path}")

# Main Program

if __name__ == "__main__":
    data = get_data(URL, PARAMS)
    
    if data is not None:
        table = make_table(data, RECORDS_KEY)
        table = tidy_data(table)
        
        print(table.head())
        
        save_data(table, RAW_FILE)