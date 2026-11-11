#!/bin/bash
TRACE_DIR="traces" # Change this if your traces are stored elsewhere
mkdir -p results_improved_stride

echo "Starting Improved Stride simulations (Sequential)..."
for trace in "$TRACE_DIR"/*.xz; do
    trace_name=$(basename "$trace" .xz)
    echo "  -> Running $trace_name..."
    ./bin/improved_stride_sim -w 50000000 -i 100000000 "$trace" > "results_improved_stride/${trace_name}.txt"
done
echo "Improved Stride simulations completed!"
