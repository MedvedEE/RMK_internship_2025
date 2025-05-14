#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import pandas as pd
from io import StringIO

walk_to_bus = 300 # (seconds) 5 min, time to walk to the bus stop
walk_from_bus = 240 # (seconds) 4 min, time to walk from the bus stop to the office
bus_ride_duration = 13 # (minutes) 780 seconds, time to ride the bus https://transport.tallinn.ee/#bus/8/a-b/00702-1/155

def fetch_and_filter_data():
    url = "https://transport.tallinn.ee/gps.txt"
    response = requests.get(url)
    
    columns = [
        "transport_type",
        "line_number",
        "latitude_raw",
        "longitude_raw",
        "speed_kmh",
        "heading_degrees",
        "vehicle_number",
        "vehicle_type",
        "vehicle_id",
        "stop_id"
    ]
    
    if response.status_code == 200:
        df = pd.read_csv(
            StringIO(response.text),
            header=None,
            names=columns
        )
        print(df.head())
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None
        

def main():
    fetch_and_filter_data()

if __name__ == "__main__":
    main()