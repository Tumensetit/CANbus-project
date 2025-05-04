import argparse
import os
import sys

from canbusdecoder.decoder import *
from canbusdecoder.stats import *

def create_arguments():
    from importlib.metadata import version, PackageNotFoundError

    try:
        __version__ = version("canbusdecoder")
    except PackageNotFoundError:
        __version__ = "unknown"

    parser = argparse.ArgumentParser(description="CAN vehicle data decoder and analyser")
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

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

def check_filename(filename):
    
    if not filename.endswith(".json"):
        filename += ".json"

    # Notify the user that default 'decoder_output.json' will be overwritten because no name given
    if filename == "decoder_output.json" and os.path.exists(filename):
        print(f"Warning: The default file '{filename}' already exists and will be always overwritten if '-o' is not used", file=sys.stderr)
        return filename  
    
    # If the file exists but is not the default 'decoder_output.json', show an error and exit
    if os.path.exists(filename):
        print(f"Error: Output file '{filename}' already exists. Please choose a different name.", file=sys.stderr)
        sys.exit(1)

    return filename

def main():
    args = create_arguments()

    # Get file names from command line arguments
    input_file = args.inputfile
    vehicle_db_file = args.dbcfile
    query = args.query
    diffpriv = args.diffpriv
    list_message_nemes = args.list_message_names
    vss = args.vss
    output_file = check_filename(args.outputfile)

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
