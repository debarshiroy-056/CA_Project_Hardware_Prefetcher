#!/bin/bash
TRACE_DIR="traces" 
mkdir -p results_spp_dev

echo "Starting SPP simulations (Strictly Sequential)..."
for trace in "$TRACE_DIR"/*.xz; do
    trace_name=$(basename "$trace" .xz)
    echo "  -> Running $trace_name..."
    ./bin/spp_dev_sim -w 50000000 -i 100000000 "$trace" > "results_spp_dev/${trace_name}.txt"
done
echo "SPP simulations completed!"
