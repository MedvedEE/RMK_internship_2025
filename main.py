#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from data_extraction import filter_trip_ids, extract_stop_ids, find_zoo_toompark_trips, sec_to_hhmm

walk_to_bus = 300 # (seconds) 5 min, time to walk to the bus stop
walk_from_bus = 240 # (seconds) 4 min, time to walk from the bus stop to the office
meeting_time_sec = 9 * 3600 + 5 * 60 # (seconds) 9:05 AM, time of the meeting


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



def main():
    data_root = "./data"
    all_trips, _ = collect_all_travel_times(data_root)
    
    print(f"Found {len(all_trips)} trips going from Zoo to Toompark:")
    durations = [trip["time_diff_minutes"] for trip in all_trips if trip["time_diff_minutes"] > 0]
    #print(f"Valid trip durations: {durations}")
    mean_duration_min = sum(durations) / len(durations)
    rita_total_commute = walk_to_bus + mean_duration_min * 60 + walk_from_bus
    print(f"Mean travel time: {mean_duration_min:.2f} minutes")
    print(f"Rita's total commute time: {rita_total_commute / 60:.2f} minutes")
    
    leave_home_at = 8 * 3600 # 08:00
    arrive_at_office = leave_home_at + rita_total_commute
    
    print(f"If Rita leaves at 08:00, she arrives at: {sec_to_hhmm(arrive_at_office)}")    
if __name__ == "__main__":
    main()