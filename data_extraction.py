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


def main():
    """
    Main function to execute the script.
    It sets the file path and calls the filter_trip_ids function.
    """
    # Set the path to the CSV file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    trips_path = os.path.join(base_dir,'data', 'trips.txt')

    matching_ids = filter_trip_ids(trips_path)
    print(f"Found {len(matching_ids)} matching trip IDs")

if __name__ == "__main__":
    main()