import argparse
import json
import sys


from decoder import *
from stats import *


parser = argparse.ArgumentParser(description="CAN vehicle data decoder and analyser")

required_group = parser.add_argument_group("Required arguments")
required_group.add_argument("-i", "--inputfile", type=str, help="Name of the file that contains the data in the specified .tsv format")
required_group.add_argument("-d", "--dbcfile", type=str, help="Name of the file that is used to decode the inputfile(ends in .dbc)")
optional_group = parser.add_argument_group("Optional arguments")
optional_group.add_argument("-q", "--query", type=str, help="Which ECUs data would you like to query? example given: BRAKE", required=False)
optional_group.add_argument("--list-message-names", action='store_true', help="List all available message names in a dbc file", required=False)
optional_group.add_argument("--diffpriv", action='store_true', help="Print experimental diffpriv mean", required=False)
optional_group.add_argument("--vss", action='store_true', help="Experimental: map DBC signals to VSS paths", required=False)
optional_group.add_argument("-o", "--outputfile", type=str, help="Output file for saving decoded data (default: decoder_output.txt)", default="decoder_output.txt")



args = parser.parse_args()

input_file = args.inputfile
vehicle_db_file = args.dbcfile
query = args.query
diffpriv = args.diffpriv
list_message_nemes = args.list_message_names
vss = args.vss

output_file = args.outputfile

decoded_lines = []
print("Reading DBC file...")
db = cantools.database.load_file(vehicle_db_file)

if (list_message_nemes == True):
    print_dbc_message_names(db)
    sys.exit(0)

decode(decoded_lines, db, input_file, query, vss)
if len(decoded_lines) == 0:
    print("No lines found.")
    sys.exit()

print("Saving the results")


if not output_file.endswith(".json"):
    output_file += ".json"

with open(output_file, 'w') as outputfile:
    json.dump(decoded_lines, outputfile, indent=2)

print(f"Decoder output file created: {output_file}")


stats_csv_file = output_file.replace(".json", "_stats.csv")
show_stats(decoded_lines, diffpriv, stats_csv_file)
