#!/usr/bin/env python3
import sys
import math

def _to_float(tok: str) -> float:
    # Be tolerant of Fortran-style 'D' exponents
    return float(tok.replace('D', 'E'))

def process_file(path: str) -> None:
    with open(path, 'r') as f:
        for lineno, line in enumerate(f, start=1):
            parts = line.split()
            if not parts:
                continue
            if len(parts) < 3:
                # Nothing to average
                continue

            col1, col2 = parts[0], parts[1]

            # Collect columns 3, 6, 9, ...
            vals = []
            for i in range(2, len(parts), 3):  # 0-based index 2 == col 3
                try:
                    vals.append(_to_float(parts[i]))
                except ValueError:
                    # Skip unparsable numbers but keep going
                    continue

            if not vals:
                continue

            n = len(vals)
            mean = sum(vals) / n
            if n > 1:
                var = sum((x - mean) ** 2 for x in vals) / (n - 1)  # sample variance
                std = math.sqrt(var)
            else:
                std = 0.0  # std undefined for n=1; report 0

            # Print: col1 col2 average std  (scientific notation like the input)
            print(f"{col1} {col2} {mean:.5E} {std:.5E}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path-to-input.txt>")
        sys.exit(1)
    process_file(sys.argv[1])


