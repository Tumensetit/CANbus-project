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
    # TODO: don't print multiple headers. Maybe do this in CSV output file writing?
    # TODO: don't print the temp fields in final output
    if diffpriv:
        stats.append(["signal name", "signal_count", "min value", "max value", "average", "TEMP: value sum", "standard deviation", "dp mean"])
    else:
        stats.append(["signal name", "signal_count", "min value", "max value", "average", "TEMP: value sum", "standard deviation"])

    for key, values in data.items():
        if key == "non_float_keys":
            continue
        if not values:
            print(f"Warning: {key} has no values! Probably a non-float key. TODO: Make sure it's printed and remove tihs line")
            continue


        signal_count = len(values)
        min_value = min(values)
        max_value = max(values)
        value_sum = sum(values)
        average = value_sum / signal_count
        stddev = statistics.stdev(values) if len(values) > 1 else 0.0

        if key in stats:
            existing = stats[key]
            existing_signal_count = existing[1]
            existing_min = existing[2]
            existing_max = existing[3]
            existing_avg = existing[4]
            existing_value_sum = existing[5]

            signal_count += existing_signal_count
            min_value = min(min_value, existing_min)
            max_value = max(max_value, existing_max)
            # helper calculations for average:
            value_sum += existing_value_sum
            average = value_sum / signal_count

            stats.remove(existing)

        if diffpriv:
            # TODO: diffpriv_stats doesn't return the mean value - yet.
            dp_mean = diffpriv_stats(key, values)
            stats.append([key, signal_count, min_value, max_value, average, value_sum, stddev, "TODO: diffpriv value here"])
        else:
            stats.append([key, signal_count, min_value, max_value, average, value_sum, stddev])

    return stats



def process_stats(stats, decoded_lines, diffpriv):
    print("DEBUG: process_stats()")
    # Temporary first step: create the data structure of stats. Overwrite with each invocation
    # Final step: add new stats from decoded_lines
    data = {}
    data["non_float_keys"] = []
    data = generate_combined_keys(data, decoded_lines)

    stats = calculate_stats(stats, data, diffpriv)

    #TODO: fix this print by returning non-float keys and printing it in statistics
    #print("Keys that have non-float values. Can't calculate standard deviation: " + str(sorted(data["non_float_keys"])))
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
