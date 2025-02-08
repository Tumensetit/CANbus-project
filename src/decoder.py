import sys
import csv
import json
import re
import cantools

def parse_canID(text):
    match = re.search(r"Ext\. ID: (\d+)", text)
    if match:
        return int(match.group(1))
    return None

def generate_output(timestamp, canID, data): # TODO: replace canID with decoded value
    output_json = {
        "unix_epoch": timestamp,
        "bo": f"TODO.. {canID}", # TODO: what should we call the BO_ value and how do we parse it?
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

# Check if the correct number of command line arguments is provided
if len(sys.argv) != 3:
    print("Usage: python3 " + sys.argv[0] + " input_file vehicle_dbc_file")
    sys.exit(1)

# Get file names from command line arguments
input_file = sys.argv[1]
vehicle_db_file = sys.argv[2]

db = cantools.database.load_file(vehicle_db_file)

textfile = open("decoder_output.txt", "w")

# Read the input qqVEP file and extract keys from the "Extra" column
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
            output = generate_output(timestamp, canID, decoded_data)
            # print(output)
            textfile.write(json.dumps(output))
            textfile.write("\n")
        except KeyError:
            continue	# TODO: what do we do with the non found values?

textfile.close()
print("Decoder output file created")







