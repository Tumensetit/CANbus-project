import sys
import csv
import json
import re
import cantools
import argparse
import statistics
from diffprivlib.tools import quantile, mean
from diffprivlib.utils import PrivacyLeakWarning

import warnings

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

def decode(decoded_lines, input_file, query, db):
    # Read the input file decode it and save to a file
    print("Decoding started...")
    with open(input_file, 'r') as input:
        reader = csv.reader(input, delimiter='\t')
        for line in reader:
            timestamp = line[0]
            # TODO: is canID the right term? BO_ in .dbc
            canID = parse_canID(line[1]) # TODO: error handling
            data = line[2]
            padded_data_bytes = bytes.fromhex(data.zfill(16)) # pad to 8-byte value
            # decode the message from the database
            try:
                decoded_data = db.decode_message(canID, padded_data_bytes)
                message = db.get_message_by_frame_id(canID)
                # TODO: query should be optional This assumes it's mandatory
                if message.name == query:
                    decoded_line = generate_output(timestamp, message.name, decoded_data)
                    decoded_lines.append(decoded_line)
            except KeyError:
                continue	# TODO: what do we do with the non found values?
    print("Decoding ready.")