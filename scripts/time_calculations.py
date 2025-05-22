#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Time-related utility functions for GTFS data analysis.
"""



def is_in_time_window(departure_time_str, start_min=450, end_min=545):
    """
    Check if the departure time is within the specified time window.
    
    Args:
        departure_time_str (str): Departure time in GTFS format (HH:MM:SS).
        start_min (int): Start of the time window in minutes since midnight.
        end_min (int): End of the time window in minutes since midnight.
    
    Returns:
        bool: True if the departure time is within the time window, False otherwise.
    """
    time_sec = change_gtfs_time_to_seconds(departure_time_str)
    return start_min * 60 <= time_sec <= end_min * 60



def change_gtfs_time_to_seconds(time_str):
    """
    Change GTFS time format to seconds since midnight.

    Args:
        time_str (str): Time string in GTFS format (HH:MM:SS).
    
    Returns:
        int: Corresponding time in seconds since midnight.
    """
    hours, minutes, seconds = map(int, time_str.split(':'))
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds


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