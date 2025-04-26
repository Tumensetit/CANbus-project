import argparse
import sys

from .decoder import *
from .stats import *

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


def main():
    args = create_arguments()

    # Get file names from command line arguments
    input_file = args.inputfile
    vehicle_db_file = args.dbcfile
    query = args.query
    diffpriv = args.diffpriv
    list_message_nemes = args.list_message_names
    vss = args.vss
    output_file = args.outputfile

    print("Reading DBC file...")
    db = cantools.database.load_file(vehicle_db_file)

    if (list_message_nemes == True):
        print_dbc_message_names(db)
        sys.exit(0)

    stats = decode(db, input_file, output_file, query, vss, diffpriv)

    print("ASDF1: " + str(stats))
    # TODO: after restructuring stats, this needs to be tested. Does this work if --query ASDF?
    if len(stats) == 0:
        print("No messages found. If using --query, use --list-message-names to list message names available in the DBC file.")
        sys.exit()

    print("TOOO: fix showing stats")
    #show_stats(stats)
    #TODO: is this renaming logic working for special cases like filename.json.txt.json and necessary in the first place?
    #should we simply append the _stats.csv?
    if not output_file.endswith(".json"):
        output_file += ".json"

    stats_csv_file = output_file.replace(".json", "_stats.csv")

    save_stats(stats, stats_csv_file)

if __name__ == "__main__":
    main()
