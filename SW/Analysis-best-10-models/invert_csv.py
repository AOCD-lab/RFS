import sys
import pandas as pd

def reorder_csv(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    columns = list(df.columns)
    if len(columns) < 2:
        print("Error: CSV must have at least 2 columns.")
        return

    id_col = columns[0]
    target_col = columns[1]
    middle_cols = columns[2:]

    # New order: all except ID and Yield, then Yield, then ID
    new_order = middle_cols + [target_col, id_col]
    df = df[new_order]

    df.to_csv(output_csv, index=False)
    print(f"Rewritten CSV saved to: {output_csv}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reorder_csv.py <input.csv> <output.csv>")
        sys.exit(1)

    reorder_csv(sys.argv[1], sys.argv[2])


