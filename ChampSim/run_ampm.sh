#!/bin/bash
mkdir -p results_ampm

BINARY="bin/1C.fullBW.ampm"
WARMUP=50000000
SIM=100000000
MAX_JOBS=3

echo "Starting parallel simulations for the AMPM configuration..."

for trace in traces/*; do
    trace_name=$(basename "$trace")
    echo "Launching AMPM run: $trace_name"
    $BINARY --warmup-instructions $WARMUP --simulation-instructions $SIM "$trace" > "results_ampm/${trace_name}.txt" &
    
    while (( $(jobs -p | wc -l) >= MAX_JOBS )); do
        sleep 5
    done
done

wait
echo "Done! All AMPM results are saved in the results_ampm/ folder."
