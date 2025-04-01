from decode import decode
from diffpriv import show_stats

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

## Main starts here
parser = argparse.ArgumentParser(description="Argument parser for Decoder")

parser.add_argument("-i", "--inputfile", type=str, help="Name of the file that contains the data to be decoded")
parser.add_argument("-d", "--dbcfile", type=str, help="Name of the file that is used to decode the inputfile(ends in .dbc)")
parser.add_argument("-q", "--query", type=str, help="Which ECUs data would you like to query? example given: BRAKE")

args = parser.parse_args()

# Get file names from command line arguments
input_file = args.inputfile
vehicle_db_file = args.dbcfile
query = args.query

db = cantools.database.load_file(vehicle_db_file)
decoded_lines = []
decode(decoded_lines, input_file, query, db)

if len(decoded_lines) == 0:
    print("No lines found.")
    sys.exit()

print("Saving the results")

# Save the output to a file
with open('decoder_output.txt', 'a') as outputfile:
    json.dump(decoded_lines, outputfile, indent=2)

print("Decoder output file created")
show_stats(decoded_lines)