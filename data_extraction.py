#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script filters and extracts specific trip IDs from a CSV file based on a given condition.
It's designed to work with GTFS data files. Currently analyzed data is from Maanteeamet
"""
import csv
import os


def filter_trip_ids(file_path):
    
    """

    Extract trip IDs from a CSV file where the trip_long_name matches 'Väike-Õismäe - Äigrumäe'. E.g. buss line 8
    Args:
        file_path (str): Path to the CSV file containing trip data.
    Returns:
        list: A list of trip IDs that match the specified condition.
    """
    matching_trip_ids = []
    
    # Opening file
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # Reading the file and filtering trip IDs
        for row in reader: 
            # Check if the trip_long_name matches the specified condition
            if (row['trip_long_name'] == 'Väike-Õismäe - Äigrumäe'):
                matching_trip_ids.append(row['trip_id'])
    
    return matching_trip_ids


def extract_stop_ids(file_path):
    """
    Extract stop IDs for 'Zoo' and 'Toompark' from a CSV file.

    Args:
        file_path (str): Path to the CSV file containing stop data.

    Returns:
        tuple: A tuple containing two lists: zoo_stop_ids and toompark_stop_ids.
    Raises:
        FileNotFoundError: If the specified file does not exist.
    """    
    zoo_stop_ids = []
    toompark_stop_ids = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if (row['stop_name'] == 'Zoo'):
                    zoo_stop_ids.append(row['stop_id'])
                elif (row['stop_name'] == 'Toompark'):
                    toompark_stop_ids.append(row['stop_id'])
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    return zoo_stop_ids, toompark_stop_ids

def find_zoo_toompark_trips(stop_times_path, zoo_stop_ids, toompark_stop_ids, start_min=480, end_min=545):
    """
    Find trips that go from Zoo to Toompark.
    Then calculate their travel time from Zoo to Toompark
    
    Args:
        stop_times_path (str): stop_times.txt file path
        zoo_stop_ids (str): Zoo stop IDs
        toompark_stop_ids (str): Toompark stop IDs

    Returns:
        list: A list of dictionaries containing trip information, including trip ID, stop IDs, and travel time.
    """
    
    trips = {}
    
    # Read stop_times.txt and group by trip_id
    with open(stop_times_path, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            trip_id = row['trip_id']
            if trip_id not in trips:
                trips[trip_id] = []
            # Saving every stop info
            trips[trip_id].append({
                'stop_id': row['stop_id'],
                'arrival_time': row['arrival_time'],
                'departure_time': row['departure_time'],
                'stop_sequence': int(row['stop_sequence'])
            })

    results = []
    
    # Start analyzing every trip
    for trip_id, stops in trips.items():
        # Finding all Zoo stops
        zoo_stops = [s for s in stops if s['stop_id'] in zoo_stop_ids]
        # Finding all Toompark stops
        toompark_stops = [s for s in stops if s['stop_id'] in toompark_stop_ids]
        
        # If there are both Zoo and Toompark stops, we can calculate the time difference
        if zoo_stops and toompark_stops:
            first_zoo = zoo_stops[0]
            subsequent_toompark = [s for s in toompark_stops 
                                if s['stop_sequence'] > first_zoo['stop_sequence']]
            
            if subsequent_toompark and is_in_time_window(first_zoo['departure_time']):
                first_toompark = subsequent_toompark[0]
                
                zoo_min = change_gtfs_time(first_zoo['departure_time'])
                toompark_min = change_gtfs_time(first_toompark['arrival_time'])
                time_diff = toompark_min - zoo_min
                
                results.append({
                    'trip_id': trip_id,
                    'zoo_stop_id': first_zoo['stop_id'],
                    'zoo_departure': first_zoo['departure_time'],
                    'toompark_stop_id': first_toompark['stop_id'],
                    'toompark_arrival': first_toompark['arrival_time'],
                    'time_diff_minutes': round(time_diff, 2),
                    'intermediate_stops': first_toompark['stop_sequence'] - first_zoo['stop_sequence'] - 1
                })
    
    return results
        
def is_in_time_window(departure_time_str, start_min=480, end_min=545):
    """
    Check if the departure time is within the specified time window.
    
    Args:
        departure_time_str (str): Departure time in GTFS format (HH:MM:SS).
        start_min (int): Start of the time window in minutes since midnight.
        end_min (int): End of the time window in minutes since midnight.
    
    Returns:
        bool: True if the departure time is within the time window, False otherwise.
    """
    departure_time = change_gtfs_time(departure_time_str)
    return start_min <= departure_time <= end_min
        
def change_gtfs_time(time_str):
    """
    Change GTFS time format to minutes since midnight.
    
    Args:
        time_str (str): Time string in GTFS format (HH:MM:SS).
    
    Returns:
        int: Corresponding time in minutes since midnight.
    """
    hours, minutes, seconds = map(int, time_str.split(':'))
    total_minutes = hours * 60 + minutes + seconds // 60
    return total_minutes

def sec_to_hhmm(seconds):
    """Convert seconds since midnight to HH:MM format

    Args:
        seconds (int): Seconds since midnight

    Returns:
        str: Time in HH:MM format
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    # Turning them into integers othwerwise they will be X.0 and ruins the time format
    return f"{int(hours):02}:{int(minutes):02}"


def main():
    """
    Main function to execute the script.
    It sets the file path and calls the filter_trip_ids function.
    """
    # Set the path to the CSV file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    trips_path = os.path.join(base_dir,'data', 'trips.txt')
    stops_path = os.path.join(base_dir,'data', 'stops.txt')
    stop_times_path = os.path.join(base_dir,'data' ,'stop_times.txt')
    
    # Check if the file exists
    for file_path in [trips_path, stops_path]:
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return

    trip_ids = filter_trip_ids(trips_path)
    print(f"Found {len(trip_ids)} matching trip IDs")
    
    print("Finding Zoo and Toompark stop IDs")
    zoo_stop_ids, toompark_stop_ids = extract_stop_ids(stops_path)
    print(f"Zoo stop IDs: {zoo_stop_ids}")
    print(f"Toompark stop IDs: {toompark_stop_ids}")
    
    # # Analyzing trips from Zoo to Toompark
    print("\nAnalyzing trips from Zoo to Toompark...")
    results = find_zoo_toompark_trips(stop_times_path, zoo_stop_ids, toompark_stop_ids)
    
    # Filtering results, because we are interested only in bus 8
    filtered_results = [r for r in results if r['trip_id'] in trip_ids]
    
    # Print the results
    print(f"\nFound {len(filtered_results)} trips going from Zoo to Toompark:")
    for trip in sorted(filtered_results, key=lambda x: x['time_diff_minutes']):
        print(f"\nTrip ID: {trip['trip_id']}")
        print(f"Departs Zoo ({trip['zoo_stop_id']}) at {trip['zoo_departure']}")
        print(f"Arrives Toompark ({trip['toompark_stop_id']}) at {trip['toompark_arrival']}")
        print(f"Travel time: {trip['time_diff_minutes']} minutes")

if __name__ == "__main__":
    main()