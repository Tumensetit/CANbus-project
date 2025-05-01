import csv
import statistics
import math

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

# Welford's algorithm for incremental calculations
def update_stats(existing_n, existing_mean, existing_M2, new_values):
    for x in new_values:
        existing_n += 1
        delta = x - existing_mean
        existing_mean += delta / existing_n
        delta2 = x - existing_mean
        existing_M2 += delta * delta2
    return existing_n, existing_mean, existing_M2

def finalize_stddev(n, M2):
    return math.sqrt(M2 / (n - 1)) if n > 1 else 0.0

def calculate_stats(stats, data, diffpriv):
    for key, values in data.items():
        if key == "non_float_keys":
            continue
        if not values:
            print(f"Warning: {key} has no values! Probably a non-float key. TODO: Make sure it's printed and remove tihs line")
            continue

        min_value = min(values)
        max_value = max(values)

        # Initialize or find existing stats entry
        existing = None
        for entry in stats:
            if isinstance(entry, list) and entry and entry[0] == key:
                existing = entry
                break

        if existing:
            existing_n = existing[1]
            existing_min = existing[2]
            existing_max = existing[3]
            existing_mean = existing[4]
            existing_M2 = existing[6]
            stats.remove(existing)
        else:
            existing_n = 0
            existing_mean = 0.0
            existing_M2 = 0.0
            existing_min = float("inf")
            existing_max = float("-inf")

        updated_n, updated_mean, updated_M2 = update_stats(existing_n, existing_mean, existing_M2, values)

        min_value = min(min_value, existing_min)
        max_value = max(max_value, existing_max)
        stddev = finalize_stddev(updated_n, updated_M2)

        if diffpriv:
            dp_mean = diffpriv_stats(key, values)
            stats.append([key, updated_n, min_value, max_value, updated_mean, stddev, updated_M2, "TODO: diffpriv value here"])
        else:
            stats.append([key, updated_n, min_value, max_value, updated_mean, stddev, updated_M2])

    return stats



def process_stats(metadata, decoded_lines, diffpriv):
    data = {}
    data["non_float_keys"] = []
    data = generate_combined_keys(data, decoded_lines)

    metadata.stats = calculate_stats(metadata.stats, data, diffpriv)

    metadata.non_float_keys.extend(sorted(data["non_float_keys"]))


    return metadata

def show_stats(metadata):
    print("Statistics: ")

    print("\t# of messages: " + str(metadata.message_count))
    duration = metadata.last_epoch - metadata.first_epoch
    print("time between first and last signal: " + str(duration) + "s")

    if duration != 0:
        print("messages/sec: " + str(metadata.message_count / duration))
    else:
        print("messages/sec: -")

    print(f"Keys that had non-float values were decoded but omitted from stats: {metadata.non_float_keys}")

def save_stats(stats, csv_output_file):
    # TODO: Do we eant to check if if exists in main, refuse to start decoding if it does?
    # This is a write and and not append so it's not a big problem
    with open(csv_output_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(stats)

    print(f"Statistics CSV saved to {csv_output_file}")
