import statistics

from diffpriv import diffpriv_stats




def show_stats(decoded_lines, diffpriv):
    print("Statistics: ")
    print("\t# of signals: " + str(len(decoded_lines)))
    first = float(decoded_lines[0]['unix_epoch'])
    last = float(decoded_lines[-1]['unix_epoch'])
    duration = last-first
    print("time between first and last signal: " + str(duration) +"s")
    print("signals/sec: " + str(len(decoded_lines)/duration))

    data = {}
    nonfloat_keys = set()

    for entry in decoded_lines:
        can_id = entry['CanID']
        for key, value in entry['signal'].items():
            combined_key = f"{can_id}/{key}"
            if combined_key not in data:
                data[combined_key] = []
            if isinstance(value, (int, float)):
                data[combined_key].append(value)
            else:
                nonfloat_keys.add(combined_key)
                continue

    print("Keys that have non-float values. Can't calculate standard deviation: " + str(sorted(nonfloat_keys)))

    print("Standard deviations (defaults to 0.0 if only one value exists:")
    for key, values in data.items():
        if len(values) > 1:  # Avoid statistics error for single-value lists
            stddev = statistics.stdev(values)
        else:
            stddev = 0.0  # Default to 0 if only one value exists
        print(f"{key}: {stddev:.6f}")

        if diffpriv == True:
            diffpriv_stats(key, values)
