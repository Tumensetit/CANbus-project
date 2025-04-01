import sys
import csv
import json
import re
import cantools
import argparse
import statistics
from diffprivlib.tools import quantile, mean
from diffprivlib.utils import PrivacyLeakWarning

import warnings

def diffpriv_values(key, data):
    # Experimental diffpriv values
    epsilon = 1.0
    # Estimate lower and upper bounds privately
    # TODO: Differential privacy ei toimi näin. Tämä on riski yksityisyydelle. Mietittävä, miten tämä oikeasti pitäisi toteutttaa
    warnings.filterwarnings("ignore", category=PrivacyLeakWarning)
    lower_bound = quantile(data, 0.05, epsilon=epsilon)
    upper_bound = quantile(data, 0.95, epsilon=epsilon)
    warnings.resetwarnings()
    if lower_bound > upper_bound:
        lower_bound, upper_bound = upper_bound, lower_bound
    dp_mean = mean(data, epsilon=epsilon, bounds=(lower_bound, upper_bound))
    print(f"Experimental: Differentially Private Mean: {key}, {dp_mean}")

def show_stats(decoded_lines):
    print("Statistics: ")
    print("\t# of signals: " + str(len(decoded_lines)))
    first = float(decoded_lines[0]['unix_epoch'])
    last = float(decoded_lines[-1]['unix_epoch'])
    duration = last-first
    print("time between first and last signal: " + str(duration) +"s")
    print("signals/sec: " + str(len(decoded_lines)/duration))

    print("Calculating standard deviations...")
    signal_keys = decoded_lines[0]['signal'].keys()
    data = {key: [] for key in signal_keys}
    for entry in decoded_lines:
        for key, value in entry['signal'].items():
            data[key].append(value)

    for key, values in data.items():
        stddev = statistics.stdev(values)
        print(f"{key}: {stddev:.6f}")
        diffpriv_values(key, value)