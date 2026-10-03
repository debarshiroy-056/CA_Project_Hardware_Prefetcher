#!/bin/bash

# Create a separate folder for stride results
mkdir -p results_stride

# Configuration variables pointing to your new stride binary
BINARY="bin/1C.fullBW.stride"
WARMUP=50000000
SIM=100000000

# Limit to 3 concurrent simulations to protect your 8GB RAM
MAX_JOBS=3

echo "Starting parallel simulations for the Stride prefetcher configuration..."

for trace in traces/*; do
    trace_name=$(basename "$trace")
    
    echo "Launching Stride run: $trace_name"
    
    $BINARY --warmup-instructions $WARMUP --simulation-instructions $SIM "$trace" > "results_stride/${trace_name}.txt" &
    
    while (( $(jobs -p | wc -l) >= MAX_JOBS )); do
        sleep 5
    done
done

wait
echo "Done! All Stride results are saved in the results_stride/ folder."
