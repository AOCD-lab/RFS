# slice_csv.py
import sys
import csv
from pathlib import Path

def _dedupe_preserve_order(seq):
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def slice_csv_all_lines(csv_path, headerfile_path):
    # Read all non-empty lines as header spec lines
    with open(headerfile_path, 'r') as f:
        raw_lines = f.readlines()

    header_lines = [ln.strip() for ln in raw_lines if ln.strip() != ""]
    num_specs = len(header_lines)

    if num_specs == 0:
        print("Error: No non-empty lines found in the headers file.")
        sys.exit(1)

    # Determine zero-padding width (at least 2, grows if N >= 100, etc.)
    pad = max(2, len(str(num_specs)))

    # Read the CSV once to get headers and cache rows
    with open(csv_path, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        all_headers = reader.fieldnames
        if not all_headers:
            print("Error: CSV appears to have no header row.")
            sys.exit(1)

        rows = list(reader)

    # First two columns by position
    first_two_cols = all_headers[:2]

    # Iterate in file order, but filenames count down so last becomes 01
    for idx, line in enumerate(header_lines, start=1):
        selected_headers = line.split()  # whitespace-separated tokens
        print(f"# Line {idx}: Found {len(selected_headers)} descriptor(s) to extract.")

        headers_to_keep = _dedupe_preserve_order(first_two_cols + selected_headers)

        # Validate columns exist
        missing = [h for h in headers_to_keep if h not in all_headers]
        if missing:
            print(f"Error (line {idx}): Missing columns in CSV: {missing}")
            continue  # skip this spec but proceed with others

        # Compute descending file index so the last line ends with _01
        file_index = num_specs - idx + 1
        out_name = f"best_{file_index:0{pad}d}.csv"

        with open(out_name, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers_to_keep)
            writer.writeheader()
            for row in rows:
                filtered = {k: row[k] for k in headers_to_keep}
                writer.writerow(filtered)

        print(f"Wrote {out_name} with columns: {headers_to_keep}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python slice_csv.py <file.csv> <headers.txt>")
        sys.exit(1)

    csv_path = sys.argv[1]
    headers_path = sys.argv[2]

    # Basic existence checks (optional but helpful)
    if not Path(csv_path).is_file():
        print(f"Error: CSV file not found: {csv_path}")
        sys.exit(1)
    if not Path(headers_path).is_file():
        print(f"Error: headers file not found: {headers_path}")
        sys.exit(1)

    slice_csv_all_lines(csv_path, headers_path)

