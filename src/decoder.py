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

def decode(decoded_lines):
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

def diffpriv_values(key, data):
    # Experimental diffpriv values
    epsilon = 1.0
    # Estimate lower and upper bounds privately
    # TODO: Differential privacy ei toimi näin. Tämä on riski yksityisyydelle. Mietittävä, miten tämä oikeasti pitäisi toteutttaa
    warnings.filterwarnings("ignore", category=PrivacyLeakWarning)
    lower_bound = quantile(data, 0.05, epsilon=epsilon)
    upper_bound = quantile(data, 0.95, epsilon=epsilon)
    warnings.resetwarnings()
    if lower_bound > upper_bound:
        lower_bound, upper_bound = upper_bound, lower_bound
    dp_mean = mean(data, epsilon=epsilon, bounds=(lower_bound, upper_bound))
    print(f"Experimental: Differentially Private Mean: {key}, {dp_mean}")



def show_stats(decoded_lines):
    print("Statistics: ")
    print("\t# of signals: " + str(len(decoded_lines)))
    first = float(decoded_lines[0]['unix_epoch'])
    last = float(decoded_lines[-1]['unix_epoch'])
    duration = last-first
    print("time between first and last signal: " + str(duration) +"s")
    print("signals/sec: " + str(len(decoded_lines)/duration))

    print("Calculating standard deviations...")
    signal_keys = decoded_lines[0]['signal'].keys()
    data = {key: [] for key in signal_keys}
    for entry in decoded_lines:
        for key, value in entry['signal'].items():
            data[key].append(value)

    for key, values in data.items():
        stddev = statistics.stdev(values)
        print(f"{key}: {stddev:.6f}")
        diffpriv_values(key, value)


## Main starts here
parser = argparse.ArgumentParser(description="Argument parser for Decoder")

parser.add_argument("-i", "--inputfile", type=str, help="Name of the file that contains the data to be decoded")
parser.add_argument("-d", "--dbcfile", type=str, help="Name of the file that is used to decode the inputfile(ends in .dbc)")
parser.add_argument("-q", "--query", type=str, help="Which ECUs data would you like to query? example given: BRAKE")

args = parser.parse_args()

# Check if the correct number of command line arguments is provided
#if len(sys.argv) != 4:
#    print("Usage: python3 " + sys.argv[0] + " input_file vehicle_dbc_file query")
#    sys.exit(1)

# Get file names from command line arguments
input_file = args.inputfile
vehicle_db_file = args.dbcfile
query = args.query

db = cantools.database.load_file(vehicle_db_file)
decoded_lines = []
decode(decoded_lines)

if len(decoded_lines) == 0:
    print("No lines found.")
    sys.exit()

print("Saving the results")
# Save the output to a file
with open('decoder_output.txt', 'a') as outputfile:
    json.dump(decoded_lines, outputfile, indent=2)

print("Decoder output file created")
show_stats(decoded_lines)

