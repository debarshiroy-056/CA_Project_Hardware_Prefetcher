#!/bin/bash
TRACE_DIR="traces" 
mkdir -p results_berti

echo "Starting Berti simulations (Sequential)..."
for trace in "$TRACE_DIR"/*.xz; do
    trace_name=$(basename "$trace" .xz)
    echo "  -> Running $trace_name..."
    ./bin/berti_sim -w 50000000 -i 100000000 "$trace" > "results_berti/${trace_name}.txt"
done
echo "Berti simulations completed!"
