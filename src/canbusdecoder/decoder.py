import json
import re
import sys
import time
from dataclasses import dataclass
from typing import List, Any

import cantools

from canbusdecoder.vss import convertDataToVss
from .stats import *



@dataclass
class Metadata:
    all_messages_count: int
    decoded_message_count: int
    first_epoch: float
    last_epoch: float
    non_float_keys: List[str]
    stats: List[List[Any]]	# holds the header and stats that will be saved as a csv
    first_entry_flag: bool # for printing output json in a memory-safe way

    def __init__(self, diffpriv):
        self.all_messages_count = 0
        self.decoded_message_count = 0
        self.first_epoch = None
        self.last_epoch = 0
        self.non_float_keys = []
        self.stats = []
        self.first_entry_flag = True

        # Create the stats file header. Column M2 is needed for Welford's algorithm. It will be removed when saving the file
        # Explanation of M2: running variance accumulator used for computing stddev with Welford's algorithm
        if diffpriv:
            self.stats.append(["signal_name", "signal count" , "min", "max", "mean", "stddev","M2","DP mean (nonincremental latest batch"])
        else:
            self.stats.append(["signal_name", "signal count" , "min", "max", "mean", "stddev","M2"])




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
        synon_floatnon_floats.exit(1)

    return first_line


def print_estimate(avg_ns_per_row, rows, x):
    remaining_rows = max(rows - x, 0)
    remaining_time_sec = (avg_ns_per_row * remaining_rows) / 1e9
    percent_done = int(100 * x / rows)
    print(f"{percent_done}% done, Estimated time remaining: {remaining_time_sec:4.0f} seconds", end='\r')

def process_lines(decoded_lines, metadata, outputfile, diffpriv):
    if len(decoded_lines) == 0:
        return metadata

    for entry in decoded_lines:
        if not metadata.first_entry_flag:
            outputfile.write(',\n')
        json.dump(entry, outputfile)
        metadata.first_entry_flag = False

    metadata = process_stats(metadata, decoded_lines, diffpriv)

    metadata.decoded_message_count += len(decoded_lines)
    if metadata.first_epoch is None:
        metadata.first_epoch = float(decoded_lines[0]['unix_epoch'])

    metadata.last_epoch = float(decoded_lines[-1]['unix_epoch'])

    decoded_lines.clear()
    return metadata

def decode(db, input_file, output_file, query, vss, diffpriv):
    decoded_lines = []
    metadata = Metadata(diffpriv)

    outputfile = open(output_file, 'a')
    outputfile.write("[\n")

    print("Opening input file...")
    with open(input_file, 'r') as input:
        #first_line_raw = input.readline()
        #first_line = first_line_raw.strip().split('\t')
        # TODO: make check_input_syntax work, make an automated test for it
        #check_input_syntax(first_line)

        rows = sum(1 for _ in input)
        metadata.all_messages_count = rows
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
            if x % 40000000 == 0 and x != 0:
                print("Dumping decoded lines to outputfile to avoid running out of memory")
                metadata = process_lines(decoded_lines, metadata, outputfile, diffpriv)

    print(f"Decoder output file created: {output_file}")
    print("Processing final stats..")
    metadata = process_lines(decoded_lines, metadata, outputfile, diffpriv)

    outputfile.write("\n]")
    outputfile.close()
    return metadata

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
