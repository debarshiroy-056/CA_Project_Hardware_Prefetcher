#!/bin/bash
TRACE_DIR="traces" 
mkdir -p results_pythia

echo "Starting Pythia simulations (Sequential)..."
for trace in "$TRACE_DIR"/*.xz; do
    trace_name=$(basename "$trace" .xz)
    echo "  -> Running $trace_name..."
    ./bin/pythia_sim -w 50000000 -i 100000000 "$trace" > "results_pythia/${trace_name}.txt"
done
echo "Pythia simulations completed!"
