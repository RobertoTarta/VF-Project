import argparse
from pathlib import Path
import subprocess
import csv
import re

def read_csv(csv_file):
    with open(csv_file, "r") as f:
        reader = csv.reader(f)
        onnx_list, vnnlib_list, time_list = zip(*reader)
    return onnx_list, vnnlib_list, time_list

def extract_sat_value_from_output(output):
    # Use regular expression to find the line containing "sat"
    sat_line = re.search(r'sat,([\d.]+)', output)
    if sat_line:
        return sat_line.group(1)
    else:
        return "Not found"

def run_command(script_path, input1_folder, input2_folder, output_file, onnx_list, vnnlib_list, time_list):
    onnx_list = [(input1_folder + x) for x in onnx_list]
    vnnlib_list = [(input2_folder + x) for x in vnnlib_list]
    time_list = [float(x) for x in time_list]

    length = len(onnx_list)

    for i in range(length):
        # Replace the following line with your command
        command = f"python3 {script_path} --net '{onnx_list[i]}' --spec '{vnnlib_list[i]}' --timeout {time_list[i]}"

        # Print a comment line with the command
        print(f"# Executing: {command}")

        # Run the command and collect the output
        output = subprocess.check_output(command, shell=True, text=True)

        #Extract sat value from the output
        sat_value = extract_sat_value_from_output(output)

        # Append the output to the output file
        with open(output_file, "a") as f:
            f.write(f"# Output for {onnx_list[i]} <-> {vnnlib_list[i]}:\n")
            f.write(f"sat,{sat_value}")
            f.write("\n")

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Iteratively execute a command with file pairs.")
    parser.add_argument("--script", required=True,help="Path to the neuralsat script file.")
    parser.add_argument("--onnx", required=True, help="Path to the first input folder.")
    parser.add_argument("--vnnlib", required=True, help="Path to the second input folder.")
    parser.add_argument("--output", required=True, help="Path to the output file.")
    parser.add_argument("--csv", required=True, help="Path to the CSV file.")
    args = parser.parse_args()

    # Read CSV file
    onnx_list, vnnlib_list, time_list = read_csv(args.csv)

    # Run the command for each file pair and append output to the output file
    run_command(args.script, args.onnx, args.vnnlib, args.output, onnx_list, vnnlib_list, time_list)

if __name__ == "__main__":
    main()
