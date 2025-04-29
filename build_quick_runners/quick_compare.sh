#!/bin/bash

clear
cd ../../jpscore/build
# Compile with ninja
echo "Compiling with ninja..."
if ! ninja; then
    echo "Compilation failed!"
    exit 1
fi
source environment

# First check if reference file exists
if [ ! -f "ref_quick_compare.sqlite" ]; then
    echo "Reference file ref_quick_test.sqlite does not exist"
    echo "Creating ref_quick_test.sqlite from build_quick_runners/quick_corridor_sim.py"
    # Create the reference file
    python ../../jupedsim_test_sandbox/build_quick_runners/quick_corridor_sim.py &> /dev/null
    cp quick_corridor_sim.sqlite ref_quick_compare.sqlite
    echo "Reference file ref_quick_compare.sqlite created"
fi

python ../../jupedsim_test_sandbox/build_quick_runners/quick_corridor_sim.py

# Compare the SQLite files
python ../../jupedsim_test_sandbox/build_quick_runners/compare_sqlite.py


