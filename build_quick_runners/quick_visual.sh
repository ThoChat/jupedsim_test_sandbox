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


python ../../jupedsim_test_sandbox/build_quick_runners/quick_corridor_sim.py

# create visual
python ../../jupedsim_test_sandbox/visualisator_humanoid_paradigm.py quick_corridor_sim.sqlite


