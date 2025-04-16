import argparse
import json
import sys


from decoder import *

def create_arguments():
    parser = argparse.ArgumentParser(description="CAN vehicle data decoder and analyser")

    required_group = parser.add_argument_group("Required arguments")
    required_group.add_argument("-i", "--inputfile", type=str, help="Name of the file that contains the data in the specified .tsv format", required=True)
    required_group.add_argument("-d", "--dbcfile", type=str, help="Name of the file that is used to decode the inputfile(ends in .dbc)", required=True)

    optional_group = parser.add_argument_group("Optional arguments")
    optional_group.add_argument("--list-message-names", action='store_true', help="List all available message names in a dbc file", required=False)
    optional_group.add_argument("-q", "--query", type=str, help="Filter result by ECU (message name). See --list-message-names.", required=False)
    optional_group.add_argument("--diffpriv", action='store_true', help="Print experimental diffpriv mean", required=False)
    optional_group.add_argument("--vss", action='store_true', help="Experimental: map DBC signals to VSS paths", required=False)

    return parser.parse_args()



args = create_arguments()

# Get file names from command line arguments
input_file = args.inputfile
vehicle_db_file = args.dbcfile
query = args.query
diffpriv = args.diffpriv
list_message_nemes = args.list_message_names
vss = args.vss

decoded_lines = []
print("Reading DBC file...")
db = cantools.database.load_file(vehicle_db_file)

if (list_message_nemes == True):
    print_dbc_message_names(db)
    sys.exit(0)

decode(decoded_lines, db, input_file, query, vss)

if len(decoded_lines) == 0:
    print("No messages found. If using --query, use --list-message-names to list message names available in the DBC file.")
    sys.exit()

print("Saving the results")
# Save the output to a file
with open('decoder_output.txt', 'a') as outputfile:
    json.dump(decoded_lines, outputfile, indent=2)

print("Decoder output file created")
show_stats(decoded_lines, diffpriv)

