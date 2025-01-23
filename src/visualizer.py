import sys
import pandas as pd
import matplotlib.pyplot as plt
import json

def main():
    # Check if the correct number of command line arguments is provided
    if len(sys.argv) != 3:
        print("Usage: python3 " + sys.argv[0] + " input_file output_file")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    timestamps, speeds = load_data(input_file)
    create_image(output_file, timestamps, speeds)

def load_data(input_file):
    timestamps = []
    speeds = []
    with open(input_file, 'r') as file:
        for line in file:
            try:
                data = json.loads(line)
                unix_epoch = float(data['unix_epoch'])
                speed = float(data['signal']['SPEED'])

                timestamps.append(unix_epoch)
                speeds.append(speed)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # toistaiseksi odottaa, että lähdeaineistossa on vain ECU 180. Filtteröinti tehdään ennen visualisointia.
                # Jos filtteröintiä ei tehdä, päädytään tähän tuhansia kertoja, ja suoritus on hidas
                print(f"Error processing line: {line.strip()} - {e}")

        return timestamps, speeds



def create_image(output_file, timestamps, speeds):
    # TODO: mietitään millaisia graafeja ylipäänsä halutaan...
    df = pd.DataFrame({'Timestamps': timestamps, 'Speeds': speeds})

    plt.figure(figsize=(10, 6))
    plt.plot(df['Timestamps'], df['Speeds'], marker='o', linestyle='-', color='b', label='Speed over Time')
    plt.xlabel('Timestamps')
    plt.ylabel('Speeds')
    plt.title('Speed vs Time')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()

    plt.savefig(output_file)
    print(f"Graph saved to {output_file}")

# guard
if __name__ == "__main__":
    main()