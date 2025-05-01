import argparse
import os
import sys

from canbusdecoder.decoder import *
from canbusdecoder.stats import *

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
    optional_group.add_argument("-o", "--outputfile", type=str, help="Output file for saving decoded data (default: decoder_output.json)", default="decoder_output.json")
    return parser.parse_args()

def get_unique_filename(filename):
    base, ext = os.path.splitext(filename)
    counter = 1
    new_filename = filename
    while os.path.exists(new_filename):
        new_filename = f"{base}_{counter}{ext}"
        counter += 1
    return new_filename


def main():
    args = create_arguments()

    # Get file names from command line arguments
    input_file = args.inputfile
    vehicle_db_file = args.dbcfile
    query = args.query
    diffpriv = args.diffpriv
    list_message_nemes = args.list_message_names
    vss = args.vss
    output_file = get_unique_filename(args.outputfile)

    print("Reading DBC file...")
    db = cantools.database.load_file(vehicle_db_file)

    if (list_message_nemes == True):
        print_dbc_message_names(db)
        sys.exit(0)

    metadata = decode(db, input_file, output_file, query, vss, diffpriv)

    if len(metadata.stats) <= 1:
        print("No messages found. If using --query, use --list-message-names to list message names available in the DBC file.")
        sys.exit()

    show_stats(metadata)

    stats_csv_file = f"{output_file}_stats.csv"

    save_stats(metadata.stats, stats_csv_file)

if __name__ == "__main__":
    main()
