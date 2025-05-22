#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script filters and extracts specific trip IDs from a CSV file based on a given condition.
It's designed to work with GTFS data files. Currently analyzed data is from Maanteeamet
"""
import csv
import os
import pandas as pd
from scripts.time_calculations import *

def filter_trip_ids(file_path):
    
    """

    Extract trip IDs from a CSV file where the trip_long_name matches 'Väike-Õismäe - Äigrumäe'. E.g. buss line 8
    Args:
        file_path (str): Path to the CSV file containing trip data.
    Returns:
        list: A list of trip IDs that match the specified condition.
    """
    matching_trip_ids = []
    """
    try:
        df = pd.read_csv(file_path)
        matching_trips = df[df['trip_long_name'] == 'Väike-Õismäe - Äigrumäe']
        return matching_trips['trip_id'].tolist()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return []
    """
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
                
                zoo_sec = change_gtfs_time_to_seconds(first_zoo['departure_time'])
                toompark_sec = change_gtfs_time_to_seconds(first_toompark['arrival_time'])
                time_diff = (toompark_sec - zoo_sec) / 60  # Convert seconds to minutes

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
        

def collect_all_travel_times(data_root):
    """Collect all travel times from the GTFS data files.

    Args:
        data_root (str): Path to the root directory containing GTFS data files.

    Returns:
        list: A list of all travel times (in minutes) from Zoo to Toompark.
        dict: A dictionary mapping each day to its corresponding travel times.
    """

    all_durations = []
    trips_durations_by_day = {}
    # Loop through each day folder in the data root directory
    # and process the GTFS data files
    for folder in sorted(os.listdir(data_root)):
        # Getting the day path
        day_path = os.path.join(data_root, folder)
        # Check if the path is a directory
        if not os.path.isdir(day_path):
            continue
        print(f"Processing day: {folder}")
        try:
            # Constructing file paths for trips, stops, and stop_times
            trips_path = os.path.join(day_path, 'trips.txt')
            stops_path = os.path.join(day_path, 'stops.txt')
            stop_times_path = os.path.join(day_path, 'stop_times.txt')
            
            # Getting the trip IDs for the day
            trips_ids = filter_trip_ids(trips_path)
            # Getting the stop IDs for Zoo and Toompark
            zoo_ids, toompark_ids = extract_stop_ids(stops_path)
            # Getting the trips from Zoo to Toompark
            trips = find_zoo_toompark_trips(stop_times_path, zoo_ids, toompark_ids)
            # Filtering the trip IDs
            filtered_trips = [t for t in trips if t['trip_id'] in trips_ids]
            
            trips_durations_by_day[folder] = filtered_trips
            all_durations.extend(filtered_trips)
        except FileNotFoundError as e:
            print(f"Failed processing day {folder}: {e}")
    return all_durations, trips_durations_by_day


def compute_lateness_probability(trips, leave_times, meeting_time_sec, walk_to_bus, walk_from_bus):
    """Compute the probability of being late for a range of departure times.

    Args:
        trips (list): List of trip information dictionaries.
        leave_times (list): List of potential departure times (in seconds).
        meeting_time_sec (int): Meeting time (in seconds).
        walk_to_bus (int): Time to walk to the bus stop (in seconds).
        walk_from_bus (int): Time to walk from the bus stop to the office (in seconds).

    Returns:
        list: List of probabilities of being late for each departure time.
    """
    probabilities = []
    for leave_home_at in leave_times:
        arrive_at_stop = leave_home_at + walk_to_bus

        # Convert GTFS strings to seconds and filter trips
        available_trips = [
            {
                "zoo_departure": change_gtfs_time_to_seconds(t["zoo_departure"]),
                "arrival_time": change_gtfs_time_to_seconds(t["toompark_arrival"]),
            }
            for t in trips
            if change_gtfs_time_to_seconds(t["zoo_departure"]) >= arrive_at_stop
        ]

        if not available_trips:
            probabilities.append(1.0)
            continue

        late_count = 0
        # Going through the available trips and checking if they are late
        # If the arrival time is greater than the meeting time, count it as late
        for trip in available_trips:
            arrival_at_office = trip["arrival_time"] + walk_from_bus
            if arrival_at_office > meeting_time_sec:
                late_count += 1

        p_late = late_count / len(available_trips)
        probabilities.append(p_late)

    return probabilities


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