#!/bin/bash

clear

# Compile with ninja
echo "Compiling with ninja..."
if ! ninja; then
    echo "Compilation failed!"
    exit 1
fi
source environment

# First check if reference file exists
if [ ! -f "ref_quick_test.sqlite" ]; then
    echo "Reference file ref_quick_test.sqlite does not exist"
    echo "Creating ref_quick_test.sqlite from quick_test.py"
    # Create the reference file
    python ../../jupedsim_test_sandbox/quick_test.py &> /dev/null
    cp quick_test.sqlite ref_quick_test.sqlite
    echo "Reference file ref_quick_test.sqlite created"
fi

python ../../jupedsim_test_sandbox/quick_test.py

# Compare the SQLite files
python ../../jupedsim_test_sandbox/compare_sqlite.py


