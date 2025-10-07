import sys
from collections import Counter

def count_descriptor_frequencies(filename):
    counter = Counter()

    with open(filename, 'r') as f:
        for line in f:
            descriptors = line.strip().split()
            counter.update(descriptors)

    # Print sorted by descending frequency
    for descriptor, freq in counter.most_common():
        print(f"{descriptor}\t{freq}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python count_descriptors.py <descriptor_file>")
        sys.exit(1)

    count_descriptor_frequencies(sys.argv[1])

