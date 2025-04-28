import json
import re
import sys
import time
from dataclasses import dataclass

import cantools

from canbusdecoder.vss import convertDataToVss
from .stats import *



# TODO: combine stats and metadata into one class
@dataclass
class Metadata:
    message_count: int
    first_epoch: float
    last_epoch: float



def parse_canID(text):
    match = re.search(r"Ext\. ID: (\d+)", text)
    if match:
        return int(match.group(1))
    return None

def generate_output(timestamp, canID, data, vss):
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

def process_lines(decoded_lines, stats, metadata, outputfile, diffpriv):
    if len(decoded_lines) == 0:
        return stats, metadata

    # Save the output to a file
    json.dump(decoded_lines, outputfile, indent=2)
    stats = process_stats(stats, decoded_lines, diffpriv)

    metadata.message_count += len(decoded_lines)
    if metadata.first_epoch == None:
        metadata.first_epoch = float(decoded_lines[0]['unix_epoch'])

    metadata.last_epoch =float(decoded_lines[-1]['unix_epoch'])
        
    decoded_lines.clear()
    return stats, metadata

def decode(db, input_file, output_file, query, vss, diffpriv):
    decoded_lines = []
    metadata = Metadata(message_count=0, first_epoch=None, last_epoch=None)
    stats = []
    if diffpriv:
        stats.append(["signal name", "signal_count", "min value", "max value", "average", "TEMP: value sum", "standard deviation", "dp mean"])
    else:
        stats.append(["signal name", "signal_count", "min value", "max value", "average", "TEMP: value sum", "standard deviation"])

    outputfile = open(output_file, 'a')

    print("Opening input file...")
    with open(input_file, 'r') as input:
        first_line_raw = input.readline()
        first_line = first_line_raw.strip().split('\t')
        #check_input_syntax(first_line)

        rows = sum(1 for _ in input) + 1  # +1 to include the first line
        input.seek(0)

        total_time = 0
        samples = 0

        print("Starting to decode...")
        for x, raw_line in enumerate(input):
            line = raw_line.strip().split('\t')

            # calculate estimate of remaining time every 1%. Check for division by zero error
            step = int(rows * 0.01)
            if step == 0:
                step = 1
            if x % step == 0:
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

            # Release memoery every now and then. 40000000 is about 3g at maximum usage
            if x % 40000000 == 0:
                stats, metadata = process_lines(decoded_lines, stats, metadata, outputfile, diffpriv)

    print(f"Decoder output file created: {output_file}")
    print("Processing final stats..")
    # TODO: possible bug: BRAKE_AMOUNT and BRAKE_PEDAL go to stats twice if there's no stats processing & docede_lines clearing before this final call..
    stats,metadata = process_lines(decoded_lines, stats, metadata, outputfile, diffpriv)

    outputfile.close()
    return stats, metadata

def decode_func(decoded_lines, line, db, query, vss):
    timestamp = line[0]
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
        pass






def get_decode_time(start, end) -> int:
    handle_time = end - start
    return handle_time #returns handle time in nanoseconds


def print_dbc_message_names(db):
    print("Available message names in the .dbc file. These can be passed to --query:")
    for message in db.messages:
        print(message.name)
