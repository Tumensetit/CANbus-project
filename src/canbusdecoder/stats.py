import csv
import statistics

from canbusdecoder.diffpriv import diffpriv_stats


def show_stats(decoded_lines, diffpriv, csv_output_file=None):
   
    first = float(decoded_lines[0]['unix_epoch'])
    last = float(decoded_lines[-1]['unix_epoch'])
    duration = last - first
   
    non_float_keys = set()

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
                non_float_keys.add(combined_key)
                continue

    print("Keys that have non-float values. Can't calculate standard deviation: " + str(sorted(non_float_keys)))

   
    headers = ["Number of signals", "Duration (s)", "Signals/sec"]
    row_values = [len(decoded_lines), duration, len(decoded_lines) / duration]

    for key, values_list in data.items():
        stddev = statistics.stdev(values_list) if len(values_list) > 1 else 0.0
        headers.append(f"{key} (SD)")
        row_values.append(stddev)

    if diffpriv and csv_output_file:
        for key, values_list in data.items():
            dp_mean = diffpriv_stats(key, values_list)
            if dp_mean is not None:
                headers.append(f"{key} (DP Mean)")
                row_values.append(dp_mean)

    if csv_output_file:
        with open(csv_output_file, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerow(row_values)
            print(f"Statistics CSV saved to {csv_output_file}")
    else:
        print("No CSV output file provided — skipping file write.")