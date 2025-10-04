import sys
import os
import subprocess
import tempfile
import pandas as pd
import numpy as np
import random

# --------------------------------------------------------------------
def load_descriptors(csv_file):
    """
    Reads the CSV file into a DataFrame and returns the DataFrame along with a list 
    of descriptor names extracted from the header (all columns from the third onward).
    """
    df = pd.read_csv(csv_file)

    if df.shape[1] < 3:
        print("Error: The CSV file must contain at least three columns (system-tag, target, and at least one descriptor).")
        sys.exit(1)

    descriptors = list(df.columns[2:])
    return df, descriptors

# --------------------------------------------------------------------
def assemble_matrix(df, selected_descriptors, matrix_head, sterics_data):
    """
    Assembles the matrix in memory instead of writing it to disk.
    Receives preloaded matrix.head and sterics.dat contents to avoid repeated I/O.
    """
    matrix_content = []

    # Append the preloaded 'matrix.head' content
    if matrix_head:
        matrix_content.append(matrix_head)
    else:
        print("Warning: 'matrix.head' is empty or not found.")

    tag_format = "{:<14}"

    # Write system-tags (first column) with header tag
    system_tag = df.columns[0]
    systems = df.iloc[:, 0].astype(str).tolist()
    matrix_content.append(tag_format.format(system_tag) + "".join([" " + s for s in systems]) + "\n")

    # Write target tag (from CSV header, col 1) and its values (second column)
    target_tag = df.columns[1]
    targets = df.iloc[:, 1].astype(str).tolist()
    matrix_content.append(tag_format.format(target_tag) + "".join([" " + t for t in targets]) + "\n")

    # Write each descriptor column
    for desc in selected_descriptors:
        descriptor_values = df[desc].astype(str).tolist()
        matrix_content.append(tag_format.format(desc) + "".join([" " + v for v in descriptor_values]) + "\n")

    # Append the preloaded 'sterics.dat' content
    if sterics_data:
        matrix_content.append(sterics_data)

    return "".join(matrix_content)

# --------------------------------------------------------------------
def run_mlr(matrix_data):
    """
    Runs MLR.x by writing matrix_data to a temporary file and passing that file as an argument.
    The temporary file is automatically deleted after execution.
    """
    try:
        mlr_path = "/scratch/cavalll/RFS/SW/Fortran/MLR-intel.x"
        if not os.path.exists(mlr_path):
            print("Error: MLR.x not found at the specified path.")
            return None

        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as temp_file:
            temp_filename = temp_file.name
            temp_file.write(matrix_data)
            temp_file.flush()

        process = subprocess.Popen(
            [mlr_path, temp_filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        os.remove(temp_filename)

        if stderr:
            print("MLR.x Error:", stderr)

        return stdout

    except Exception as e:
        print(f"Subprocess Execution Error: {e}")
        return None

# --------------------------------------------------------------------
def check_pairwise_correlation(df, selected_descriptors, threshold):
    """
    Check max absolute pairwise correlation for selected descriptors.
    Returns True if max correlation <= threshold, otherwise False.
    """
    corr_matrix = df[selected_descriptors].corr().abs()
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    max_corr = upper.max().max()
    return max_corr <= threshold

# --------------------------------------------------------------------
def run_mc_steps(df, descriptors, num_descriptors, mc_steps, matrix_head, sterics_data, max_pw=None):
    """
    Performs Monte Carlo steps, assembling the matrix with preloaded matrix.head and sterics.dat.
    Skips selections with high pairwise correlation if max_pw is provided.
    """
    step = 0
    attempts = 0
    while step < mc_steps:
        attempts += 1
        selected_descriptors = sorted(random.sample(descriptors, num_descriptors))

        # Check pairwise correlation filter
        if max_pw is not None:
            if not check_pairwise_correlation(df, selected_descriptors, max_pw):
              # print(f"Step {step}: Skipped set {selected_descriptors} (max correlation > {max_pw})")
                continue  # retry without incrementing step

        # Assemble matrix
        matrix_data = assemble_matrix(df, selected_descriptors, matrix_head, sterics_data)

        # Run MLR
        mlr_output = run_mlr(matrix_data)
        if mlr_output is None:
            print(f"Step {step}: MLR.x execution failed.")
            continue

        # Extract Max R2
        max_r2 = ""
        for line in mlr_output.splitlines():
            if line.startswith("Max "):
                max_r2 = line.strip()
                break

        print(f"Step {step}: {selected_descriptors} | {max_r2}")
        step += 1

# ----------------------   Main below   ----------------------   
def main():
    """
    Handles command-line arguments, loads the CSV data, and performs the Monte Carlo descriptor selection.
    Usage:
      python mc-final.py <csv_file> <N_descriptors> <N_MC_steps> <MC_seed> [--maxpw <threshold>]
    """
    if len(sys.argv) < 5:
        print("Usage: python mc-final.py <csv_file> <N_descriptors> <N_MC_steps> <MC_seed> [--maxpw <threshold>]")
        sys.exit(1)

    csv_file = sys.argv[1]
    try:
        N_of_descriptors = int(sys.argv[2])
        MC_steps = int(sys.argv[3])
        MC_seed = int(sys.argv[4])
    except ValueError:
        print("Error: <N_descriptors>, <N_MC_steps>, and <MC_seed> must be integers.")
        sys.exit(1)

    # Optional argument for max pairwise correlation
    max_pw = None
    args = sys.argv[5:]
    if "--maxpw" in args:
        i = args.index("--maxpw")
        max_pw = float(args[i + 1])

    if not os.path.isfile(csv_file):
        print(f"Error: File '{csv_file}' not found.")
        sys.exit(1)

    random.seed(MC_seed)

    # Load CSV and descriptors
    df, descriptors = load_descriptors(csv_file)

    if len(descriptors) < N_of_descriptors:
        print(f"Error: The CSV file contains only {len(descriptors)} descriptors, but {N_of_descriptors} are requested.")
        sys.exit(1)

    # Load matrix.head and sterics.dat
    if not os.path.isfile("matrix.head"):
        print("Warning: 'matrix.head' does not exist.")
        sys.exit(1)
    if not os.path.isfile("sterics.dat"):
        print("Warning: 'sterics.dat' does not exist.")
        sys.exit(1)

    with open("matrix.head", "r") as f:
        matrix_head = f.read()
    with open("sterics.dat", "r") as f:
        sterics_data = f.read()

    # Run Monte Carlo loop
    run_mc_steps(df, descriptors, N_of_descriptors, MC_steps, matrix_head, sterics_data, max_pw)

# ------------------  Run main  --------------------------
if __name__ == "__main__":
    main()

