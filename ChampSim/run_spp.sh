#!/bin/bash
mkdir -p results_spp

BINARY="bin/1C.fullBW.spp"
WARMUP=50000000
SIM=100000000
MAX_JOBS=3

echo "Starting parallel simulations for the SPP configuration..."

for trace in traces/*; do
    trace_name=$(basename "$trace")
    echo "Launching SPP run: $trace_name"
    $BINARY --warmup-instructions $WARMUP --simulation-instructions $SIM "$trace" > "results_spp/${trace_name}.txt" &
    
    while (( $(jobs -p | wc -l) >= MAX_JOBS )); do
        sleep 5
    done
done

wait
echo "Done! All SPP results are saved in the results_spp/ folder."
