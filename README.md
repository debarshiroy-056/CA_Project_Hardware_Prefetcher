Markdown
# ChampSim L2 Cache Prefetcher Evaluation

This repository contains the experimental pipeline, configuration files, and analysis scripts used to evaluate L2 cache prefetchers in ChampSim. The study compares a no-prefetch baseline against several L2 prefetcher designs, including Stride, SPP, and AMPM, using a set of SPEC CPU, graph analytics, and AI workload traces.

## Project Overview

- Simulator: ChampSim
- Workloads: SPEC CPU, Ligra graph traces, and Llama2-style AI traces
- Simulation length: 50M warmup instructions, 100M simulated instructions
- Hardware target: macOS on Apple Silicon with 8 GB unified memory
- L1D prefetching: Disabled for all configurations to isolate L2 caching behavior

---

## 1. Environment Setup

ChampSim depends on the native macOS `clang++` toolchain. If you are using Miniconda or Anaconda, avoid using the Conda-provided C++ compiler because it may trigger failures related to `from_chars_floating_point.h`.

Before building the simulator, make sure you are outside the Conda environment:

```bash
conda deactivate
make clean
```

---

## 2. Build the Simulator

The project includes four prefetcher configurations, each defined by a JSON config and built into a separate binary in the `bin/` directory.

### 2.1 Baseline (No Prefetching)

```bash
./config.sh baseline_config.json
make
```

### 2.2 Stride Prefetcher

```bash
./config.sh stride_config.json
make
```

### 2.3 SPP Prefetcher

```bash
./config.sh spp_config.json
make
```

### 2.4 AMPM Prefetcher

```bash
./config.sh ampm_config.json
make
```

All successful builds are stored under the `bin/` directory.

---

## 3. Run Simulations

To avoid memory pressure and excessive swapping on the 8 GB host, the provided shell scripts run simulations with a limited concurrency level (`MAX_JOBS=3`).

Make the scripts executable:

```bash
chmod +x run_baseline.sh run_stride.sh run_spp.sh run_ampm.sh
```

Run each batch sequentially. Do not execute them in parallel:

```bash
./run_baseline.sh
./run_stride.sh
./run_spp.sh
./run_ampm.sh
```

Simulation outputs are written to their respective `results_<config>/` directories.

---

## 4. Extract Results

After the simulation runs finish, extract the raw ChampSim output into a structured CSV summary. The parser collects IPC, L2 cache misses, MPKI, prefetcher accuracy, coverage, and DRAM traffic statistics.

```bash
python3 parse_results.py
```

This generates the file:

```text
simulation_summary.csv
```

---

## 5. Generate Visualizations

The repository includes plotting scripts built with `pandas` and `matplotlib`. These scripts automatically ignore incomplete or failed runs and format plots for report-quality output.

Run the visualization suite:

```bash
python3 plot_results.py
```

```bash
python3 plot_mpki.py
```

```bash
python3 plot_acc_cov.py
```

```bash
python3 plot_dram.py
```

The generated charts are saved in the `plots/` directory, including:

- `ipc_speedup.png`
- `l2c_mpki.png`
- `pf_accuracy.png`
- `pf_coverage.png`
- `normalized_dram_traffic.png`

---

## 6. Expected Anomalies and Edge Cases

Some prefetchers may fail or produce incomplete output on irregular memory traces. These cases are expected in aggressive simulator workloads.

- SPP: The `spp_dev` prefetcher can trigger an internal assertion failure (`Abort trap: 6` in `update_entry()`) on specific graph and AI traces.
- AMPM: The virtual-address AMPM prefetcher may fail to emit standard statistics on some memory-heavy SPEC traces such as `bwaves`, `mcf`, and `lbm`.

The parsing logic tags these runs as failed or incomplete and excludes them from normalized comparisons to preserve result integrity.

---

## 7. Quick Start

If you want to reproduce the full workflow in order, use:

```bash
conda deactivate
make clean
./config.sh baseline_config.json
make
./config.sh stride_config.json
make
./config.sh spp_config.json
make
./config.sh ampm_config.json
make
chmod +x run_baseline.sh run_stride.sh run_spp.sh run_ampm.sh
./run_baseline.sh
./run_stride.sh
./run_spp.sh
./run_ampm.sh
python3 parse_results.py
python3 plot_results.py
python3 plot_mpki.py
python3 plot_acc_cov.py
python3 plot_dram.py
```

---

## 8. Notes

- Keep the simulation jobs sequential to avoid system instability.
- Use macOS-native build tools for compatibility.
- Review `results_*` directories after each run for completeness before plotting.
