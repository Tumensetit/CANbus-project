import csv
import statistics

from diffpriv import diffpriv_stats




def show_stats(decoded_lines, diffpriv, csv_output_file=None):
    print("Statistics: ")
    print("\t# of signals: " + str(len(decoded_lines)))
    first = float(decoded_lines[0]['unix_epoch'])
    last = float(decoded_lines[-1]['unix_epoch'])
    duration = last - first
    print("time between first and last signal: " + str(duration) + "s")
    print("signals/sec: " + str(len(decoded_lines) / duration))

    csv_data = []
    if csv_output_file:
        csv_data.append(["Metric", "Value"])
        csv_data.append(["# of signals", len(decoded_lines)])
        csv_data.append(["Duration (s)", duration])
        csv_data.append(["Signals/sec ", len(decoded_lines) / duration])

    data = {}

    for entry in decoded_lines:
        can_id = entry['CanID']
        for key, value in entry['signal'].items():
            combined_key = f"{can_id}.{key}"
            if combined_key not in data:
                data[combined_key] = []
            if isinstance(value, (int, float)):
                data[combined_key].append(value)
            else:
                continue

    for key, values in data.items():
        stddev = statistics.stdev(values) if len(values) > 1 else 0.0
        print(f"{key}: {stddev:.6f}")
        if csv_output_file:
            csv_data.append([f"{key} (Standard Deviation)", stddev])

        if diffpriv:
            dp_mean = diffpriv_stats(key, values)
            if dp_mean is not None and csv_output_file:
                csv_data.append([f"{key} (DP Mean)", dp_mean])

    if csv_output_file:
        with open(csv_output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(csv_data)
        print(f"Statistics CSV saved to {csv_output_file}")

