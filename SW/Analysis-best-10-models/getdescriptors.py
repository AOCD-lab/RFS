import sys
import re

def extract_dnnn_from_line(line):
    match = re.search(r"\[([^\]]+)\]", line)
    if not match:
        return []
    raw_items = match.group(1).split(',')
    return [item.strip().strip("'\"") for item in raw_items]

def main(filename):
    with open(filename, 'r') as f:
        for line in f:
            dnnn_values = extract_dnnn_from_line(line)
            if dnnn_values:
                print(" ".join(dnnn_values))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_dnnn_from_file.py <input_file>")
        sys.exit(1)

    main(sys.argv[1])

