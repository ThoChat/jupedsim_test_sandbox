#!/bin/bash

# Clear the terminal
clear

# Change directory
cd ../jpscore/build || { echo "Failed to change directory"; exit 1; }

# Compile with ninja
echo "Compiling with ninja..."
if ! ninja; then
    echo "Compilation failed!"
    exit 1
fi

# Source the environment file
if [ -f environment ]; then
    source environment
else
    echo "Environment file not found!"
    exit 1
fi

# Check if a Python file name was provided
if [ -z "$1" ]; then
    echo "No simulation provided."
    exit 1
fi

# Execute the Python file
cd ../../jupedsim_test_sandbox || { echo "Failed to change directory"; exit 1; }
python "$1"