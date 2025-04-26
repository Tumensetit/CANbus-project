import csv
import statistics

from canbusdecoder.diffpriv import diffpriv_stats


def generate_combined_keys(data, decoded_lines):
    for entry in decoded_lines:
        can_id = entry['CanID']
        for key, value in entry['signal'].items():
            combined_key = f"{can_id}.{key}"
            if combined_key not in data:
                data[combined_key] = []
            if isinstance(value, (int, float)):
                data[combined_key].append(value)
            else:
                if combined_key not in data["non_float_keys"]:
                    data["non_float_keys"].append(combined_key)

    return data

def calculate_stats(stats, data, diffpriv):
    # NOTE: we want to append to stats lines, not create new ones with each invocation
    for key, values in data.items():
        if key == "non_float_keys":
            continue

        stddev = statistics.stdev(values) if len(values) > 1 else 0.0

        dp_mean = "0"
        if diffpriv:
            dp_mean = diffpriv_stats(key, values)
            if dp_mean is not None:
                print("TODO: how do we add optional values to stats?")

        stats.append([key,stddev,dp_mean])

    return stats
    



def process_stats(stats, decoded_lines, diffpriv):
    print("DEBUG: process_stats()")
    # Temporary first step: create the data structure of stats. Overwrite with each invocation
    # Final step: add new stats from decoded_lines
    data = {}
    data["non_float_keys"] = []
    data = generate_combined_keys(data, decoded_lines)
    #TODO: fix this print
    print("Keys that have non-float values. Can't calculate standard deviation: " + str(sorted(data["non_float_keys"])))
    stats = calculate_stats(stats, data, diffpriv)
    
    return stats

def show_metadata_stats(stats):
    # TODO: in addition to stats about the signals, , we need some sort of metadata structure for these
    print("Statistics: ")

    signal_count = len(stats)
    print("\t# of signals: " + str(signal_count))

    first = float(stats[0]['unix_epoch'])
    last = float(stats[-1]['unix_epoch'])
    duration = last - first
    print("time between first and last signal: " + str(duration) + "s")

    print("signals/sec: " + str(signal_count / duration))

def save_stats(stats, csv_output_file):
    # TODO: Do we eant to check if if exists in main, refuse to start decoding if it does?
    # This is a write and and not append so it's not a big problem
    with open(csv_output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(stats)

    print(f"Statistics CSV saved to {csv_output_file}")
