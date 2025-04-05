import argparse
import json
import sys


from decoder import *



parser = argparse.ArgumentParser(description="CAN vehicle data decoder and analyser")

required_group = parser.add_argument_group("Required arguments")
required_group.add_argument("-i", "--inputfile", type=str, help="Name of the file that contains the data in the specified .tsv format")
required_group.add_argument("-d", "--dbcfile", type=str, help="Name of the file that is used to decode the inputfile(ends in .dbc)")
optional_group = parser.add_argument_group("Optional arguments")
optional_group.add_argument("-q", "--query", type=str, help="Which ECUs data would you like to query? example given: BRAKE", required=False)
optional_group.add_argument("--diffpriv", action='store_true', help="Print experimental diffpriv mean", required=False)

args = parser.parse_args()


# Check if the correct number of command line arguments is provided
#if len(sys.argv) != 4:
#    print("Usage: python3 " + sys.argv[0] + " input_file vehicle_dbc_file query")
#    sys.exit(1)

# Get file names from command line arguments
input_file = args.inputfile
vehicle_db_file = args.dbcfile
query = args.query
diffpriv = args.diffpriv

decoded_lines = []
print("Reading DBC file...")
db = cantools.database.load_file(vehicle_db_file)
decode(decoded_lines, db, input_file, query)

if len(decoded_lines) == 0:
    print("No lines found.")
    sys.exit()

print("Saving the results")
# Save the output to a file
with open('decoder_output.txt', 'a') as outputfile:
    json.dump(decoded_lines, outputfile, indent=2)

print("Decoder output file created")
show_stats(decoded_lines, diffpriv)

