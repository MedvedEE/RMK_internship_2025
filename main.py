#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import matplotlib.pyplot as plt
import numpy as np
from data_extraction import  sec_to_hhmm, collect_all_travel_times,compute_lateness_probability

WALK_TO_BUS = 300 # (seconds) 5 min, time to walk to the bus stop
WALK_FROM_BUS = 240 # (seconds) 4 min, time to walk from the bus stop to the office
MEETING_TIME_SEC = 9 * 3600 + 5 * 60 # (seconds) 9:05 AM, time of the meeting


def plot_lateness_probabilities(leave_times, probabilities):
    """Plot the probability of being late for different departure times.

    Args:
        leave_times (list): List of potential departure times (in seconds).
        probabilities (list): List of probabilities of being late for each departure time.
    """
    times_labels = [sec_to_hhmm(t) for t in leave_times]
    plt.figure(figsize=(10, 5))
    plt.plot(times_labels, probabilities, marker='o', linestyle='-', color='red')
    plt.xticks(rotation=45)
    plt.xlabel("Home departure time")
    plt.ylabel("Probability of being late")
    plt.title("Rita's Probability of Being Late vs. Departure Time")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    data_root = "./data"
    trips, _ = collect_all_travel_times(data_root)

    valid_durations = [t["time_diff_minutes"] for t in trips if t["time_diff_minutes"] > 0]
    median_dur = np.median(valid_durations)
    total_commute = WALK_TO_BUS + median_dur * 60 + WALK_FROM_BUS
    print(f"Median travel time: {median_dur:.2f} min")
    print(f"Estimated total commute: {total_commute / 60:.2f} min")

    leave_times = list(range(7 * 3600 + 30 * 60, MEETING_TIME_SEC + 1, 5 * 60))  # 07:30 → 09:05
    probs = compute_lateness_probability(trips, leave_times, MEETING_TIME_SEC, WALK_TO_BUS, WALK_FROM_BUS)
    plot_lateness_probabilities(leave_times, probs)

if __name__ == "__main__":
    main()