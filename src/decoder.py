import csv
import re
import sys
import time

import cantools
import statistics

from diffpriv import diffpriv_stats




def parse_canID(text):
    match = re.search(r"Ext\. ID: (\d+)", text)
    if match:
        return int(match.group(1))
    return None

def generate_output(timestamp, canID, data): # TODO: replace canID with decoded value
    output_json = {
        "unix_epoch": timestamp,
        "CanID": canID,
        "signal": convert_serializable(data)
    }

    return output_json

def convert_serializable(data):
    if isinstance(data, (int, float, str, bool)):
        return data
    elif isinstance(data, dict):
        return {key: convert_serializable(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_serializable(item) for item in data]
    else:
        return str(data)

def decode(decoded_lines, db, input_file, query):
    # Read the input file decode it and save to a file
    print("Decoding started...")
    with open(input_file, 'r') as input:
        reader = csv.reader(input, delimiter='\t')

        errormsg = "ERROR: Input file does not appear to be a valid TSV file. Have you ran tshark to convert .pcapng to a .tsv?  Check that the input file contains the tshark fields time_epoch, can and data"
        try:
          first_line = next(reader, None)
        except UnicodeError:
            print(errormsg)
            sys.exit(1)

        if not first_line or len(first_line) < 3 or "ID: " not in first_line[1]:
            print(errormsg)
            sys.exit(1)

        rows = sum(1 for row in reader) + 1
        input.seek(0)
        reader = csv.reader(input, delimiter='\t')

        handle_time = get_decode_time(first_line, db, decoded_lines, query)
        estimate = float(handle_time * 10**-9 * rows) # Estimated time in seconds
        print("Estimated decode time: %f seconds" %estimate)
        i = 1
        for x, line in enumerate(reader):
            if x % int(rows*0.1) == 0:
                print(f"{i*10}% done", end='\r')
                i += 1
            timestamp = line[0]
            # TODO: is canID the right term? BO_ in .dbc
            canID = parse_canID(line[1]) # TODO: error handling
            data = line[2]
            padded_data_bytes = bytes.fromhex(data.zfill(16)) # pad to 8-byte value
            # decode the message from the database
            try:
                decoded_data = db.decode_message(canID, padded_data_bytes)
                message = db.get_message_by_frame_id(canID)
                if query == None or message.name == query:
                    decoded_line = generate_output(timestamp, message.name, decoded_data)
                    decoded_lines.append(decoded_line)
            except KeyError:
                continue	# TODO: what do we do with the non found values?
    print("Decoding ready.")

def get_decode_time(line, db, decoded_lines, query) -> int:
    start = time.perf_counter_ns()
    timestamp = line[0]
    canID = parse_canID(line[1])
    data = line[2]
    padded_data_bytes = bytes.fromhex(data.zfill(16)) # pad to 8-byte value
    # decode the message from the database
    try:
        decoded_data = db.decode_message(canID, padded_data_bytes)
        message = db.get_message_by_frame_id(canID)
        if query == None or message.name == query:
            decoded_line = generate_output(timestamp, message.name, decoded_data)
            decoded_lines.append(decoded_line)
    except KeyError:
        print("Error while getting handle time")
    end = time.perf_counter_ns()
    handle_time = end - start
    return handle_time #returns handle time in nanoseconds

def show_stats(decoded_lines, diffpriv):
    print("Statistics: ")
    print("\t# of signals: " + str(len(decoded_lines)))
    first = float(decoded_lines[0]['unix_epoch'])
    last = float(decoded_lines[-1]['unix_epoch'])
    duration = last-first
    print("time between first and last signal: " + str(duration) +"s")
    print("signals/sec: " + str(len(decoded_lines)/duration))

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
                print(f"Non-numerical value \"{value}\" for {combined_key}, cannot calculate standard deviation")

    for key, values in data.items():
        if len(values) > 1:  # Avoid statistics error for single-value lists
            stddev = statistics.stdev(values)
        else:
            stddev = 0.0  # Default to 0 if only one value exists
        print(f"{key}: {stddev:.6f}")

        if diffpriv == True:
            diffpriv_stats(key, values)



def print_dbc_message_names(db):
    print("Available message names in the .dbc file. These can be passed to --query:")
    for message in db.messages:
        print(message.name)