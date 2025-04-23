import csv
import re
import sys
import time

import cantools

from canbusdecoder.vss import convertDataToVss




def parse_canID(text):
    match = re.search(r"Ext\. ID: (\d+)", text)
    if match:
        return int(match.group(1))
    return None

def generate_output(timestamp, canID, data, vss): # TODO: replace canID with decoded value
    converted_data = convert_serializable(convertDataToVss(data) if vss else data)

    output_json = {
        "unix_epoch": timestamp,
        "CanID": canID,
        "signal": converted_data
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

def check_input_syntax(reader):
    errormsg = "ERROR: Input file does not appear to be a valid TSV file. Have you ran tshark to convert .pcapng to a .tsv?  Check that the input file contains the tshark fields time_epoch, can and data"
    try:
      first_line = next(reader, None)
    except UnicodeError:
        print(errormsg)
        sys.exit(1)

    if not first_line or len(first_line) < 3 or "ID: " not in first_line[1]:
        print(errormsg)
        sys.exit(1)

    return first_line


def print_estimate(avg_ns_per_row, rows, x):
    remaining_rows = max(rows - x, 0)
    remaining_time_sec = (avg_ns_per_row * remaining_rows) / 1e9
    percent_done = int(100 * x / rows)
    print(f"{percent_done}% done, Estimated time remaining: {remaining_time_sec:4.0f} seconds", end='\r')

def decode(decoded_lines, db, input_file, query, vss):
    # Read the input file decode it and save to a file
    print("Decoding started...")
    with open(input_file, 'r') as input:
        reader = csv.reader(input, delimiter='\t')
        first_line = check_input_syntax(reader)

        rows = sum(1 for row in reader) + 1
        input.seek(0)
        reader = csv.reader(input, delimiter='\t')

        total_time = 0
        samples = 0
        for x, line in enumerate(reader):
            if x % int(rows*0.01) == 0:
                start = time.perf_counter_ns()
                decode_func(decoded_lines, line, db, query, vss)
                end = time.perf_counter_ns()
                handle_time = get_decode_time(start, end)
                total_time += handle_time
                samples += 1
                avg_time = total_time // samples
                print_estimate(avg_time, rows, x)
            else:
                decode_func(decoded_lines, line, db, query, vss)
    print() #creates newline for next print
    print("Decoding ready.")

def decode_func(decoded_lines, line, db, query, vss):
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
            decoded_line = generate_output(timestamp, message.name, decoded_data, vss)
            decoded_lines.append(decoded_line)
    except KeyError:
        pass	# TODO: what do we do with the non found valu






def get_decode_time(start, end) -> int:
    handle_time = end - start
    return handle_time #returns handle time in nanoseconds


def print_dbc_message_names(db):
    print("Available message names in the .dbc file. These can be passed to --query:")
    for message in db.messages:
        print(message.name)
