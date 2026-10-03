#!/bin/bash

# Create a folder to store all the final text file outputs
mkdir -p results_baseline

# Configuration variables
BINARY="bin/1C.fullBW.nopref"
WARMUP=50000000
SIM=100000000

# Limit to 3 concurrent simulations to prevent running out of 8GB RAM
MAX_JOBS=3

echo "Starting parallel simulations for the baseline configuration..."

for trace in traces/*; do
    # Extract just the filename to name our output text file
    trace_name=$(basename "$trace")
    
    echo "Launching: $trace_name"
    
    # Run ChampSim in the background (&) and save output (>) to a text file
    $BINARY --warmup-instructions $WARMUP --simulation-instructions $SIM "$trace" > "results_baseline/${trace_name}.txt" &
    
    # Pause the loop if we currently have 3 jobs running
    while (( $(jobs -p | wc -l) >= MAX_JOBS )); do
        sleep 5
    done
done

# Wait for the final batch of simulations to finish
echo "All traces queued. Waiting for the final simulations to complete..."
wait

echo "Done! All baseline results are saved in the results_baseline/ folder."
