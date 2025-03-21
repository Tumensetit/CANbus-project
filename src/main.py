import sys
import argparse

from diffpriv import diffpriv_stats
from decoder import *



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

decoded_lines = []
decode(decoded_lines, vehicle_db_file, input_file, query)

if len(decoded_lines) == 0:
    print("No lines found.")
    sys.exit()

print("Saving the results")
# Save the output to a file
with open('decoder_output.txt', 'a') as outputfile:
    json.dump(decoded_lines, outputfile, indent=2)

print("Decoder output file created")
show_stats(decoded_lines)

