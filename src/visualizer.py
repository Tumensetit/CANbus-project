import sys
import pandas as pd
import matplotlib.pyplot as plt

# Check if the correct number of command line arguments is provided
if len(sys.argv) != 3:
    print("Usage: python3 " + sys.argv[0] + " input_file output_file")
    sys.exit(1)

# Get file names from command line arguments
input_file = sys.argv[1]
output_file = sys.argv[2]

# TODO: lue arvot canbus-jsonista. Nyt kovakoodattuina:
timestamps = [1736342847.985590123, 1736342847.986342700, 1736342847.987495605, 1736342847.988138819,
              1736342847.988842665, 1736342847.990134583, 1736342847.990648224, 1736342847.991185636,
              1736342847.991758039, 1736342847.992447984]
speeds = [1.35, 1.41, 1.53, 1.57, 1.59, 1.71, 1.73, 1.79, 1.81, 1.82]

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
