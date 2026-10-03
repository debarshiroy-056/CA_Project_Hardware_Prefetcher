import os
import re
import pandas as pd

import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['mathtext.fontset'] = 'stix' # Matches Times for math symbols

configs = ['baseline', 'stride', 'spp', 'ampm']
results = []

for cfg in configs:
    folder = f"results_{cfg}"
    if not os.path.exists(folder):
        continue
    
    for fname in sorted(os.listdir(folder)):
        if not fname.endswith(".txt"):
            continue
        filepath = os.path.join(folder, fname)
        trace_name = fname.replace(".txt", "")
        
        with open(filepath, 'r', errors='ignore') as f:
            content = f.read()
        
        # Check if the run finished completely
        if "Cumulative IPC:" not in content and "cumulative IPC:" not in content:
            results.append({
                "Config": cfg,
                "Trace": trace_name,
                "Status": "Failed/Incomplete",
                "IPC": None,
                "L2C_Miss": None,
                "L2C_MPKI": None,
                "PF_Issued": None,
                "PF_Useful": None,
                "PF_Accuracy": None,
                "DRAM_Traffic": None
            })
            continue

        # Extract IPC
        ipc_match = re.search(r"(?:Cumulative IPC|cumulative IPC):\s*([0-9\.]+)", content)
        ipc = float(ipc_match.group(1)) if ipc_match else None

        # Extract Instructions
        inst_match = re.search(r"CPU 0 cumulative instructions:\s*(\d+)", content)
        instructions = int(inst_match.group(1)) if inst_match else 100000000

        # Extract L2C Demand Misses
        l2c_miss = None
        l2_section = re.search(r"L2C TOTAL\s+ACCESS:\s+\d+\s+HIT:\s+\d+\s+MISS:\s+(\d+)", content)
        if l2_section:
            l2c_miss = int(l2_section.group(1))
        else:
            # Fallback search for specific cache line format
            l2_miss_match = re.search(r"L2C.*?LOAD\s+ACCESS:\s+\d+\s+HIT:\s+\d+\s+MISS:\s+(\d+)", content, re.DOTALL)
            if l2_miss_match:
                l2c_miss = int(l2_miss_match.group(1))

        # Calculate MPKI
        mpki = (l2c_miss / (instructions / 1000.0)) if l2c_miss is not None else None

        # Extract Prefetch Stats (Useful / Issued)
        pf_useful_match = re.search(r"L2C PREFETCH\s+REQUESTED:\s+\d+\s+ISSUED:\s+(\d+)\s+USEFUL:\s+(\d+)", content)
        pf_issued = int(pf_useful_match.group(1)) if pf_useful_match else 0
        pf_useful = int(pf_useful_match.group(2)) if pf_useful_match else 0
        accuracy = (pf_useful / pf_issued) if pf_issued > 0 else 0.0

        # Extract DRAM traffic from row-buffer hits and misses. The output
        # reports the hit/miss counts on separate lines for each channel.
        dram_reads = re.findall(
            r"Channel\s+\d+\s+RQ ROW_BUFFER_HIT:\s*(\d+)\s*"
            r"\n\s*ROW_BUFFER_MISS:\s*(\d+)",
            content,
        )
        dram_writes = re.findall(
            r"Channel\s+\d+\s+WQ ROW_BUFFER_HIT:\s*(\d+)\s*"
            r"\n\s*ROW_BUFFER_MISS:\s*(\d+)",
            content,
        )

        total_dram = sum(
            int(hit) + int(miss)
            for hit, miss in dram_reads + dram_writes
        )

        results.append({
            "Config": cfg,
            "Trace": trace_name,
            "Status": "Success",
            "IPC": ipc,
            "L2C_Miss": l2c_miss,
            "L2C_MPKI": round(mpki, 4) if mpki is not None else None,
            "PF_Issued": pf_issued,
            "PF_Useful": pf_useful,
            "PF_Accuracy": round(accuracy * 100, 2),
            "DRAM_Traffic": total_dram
        })

df = pd.DataFrame(results)
df.to_csv("simulation_summary.csv", index=False)
print(df.to_string())
print("\nResults successfully saved to simulation_summary.csv")
