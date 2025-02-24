import sys
import csv
import json
import re
import cantools
import statistics

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

## Main starts here
# Check if the correct number of command line arguments is provided
if len(sys.argv) != 4:
    print("Usage: python3 " + sys.argv[0] + " input_file vehicle_dbc_file query")
    sys.exit(1)

# Get file names from command line arguments
input_file = sys.argv[1]
vehicle_db_file = sys.argv[2]
query = sys.argv[3]

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

