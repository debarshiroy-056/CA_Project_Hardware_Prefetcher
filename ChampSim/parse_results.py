import os
import re
import pandas as pd

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
        
        # Check if the simulation phase finished completely
        sim_match = re.search(
            r"Simulation (?:finished|complete) CPU 0 instructions:\s*(\d+)\s+cycles:\s*\d+\s+cumulative IPC:\s*([0-9\.]+)",
            content
        )
        if not sim_match:
            results.append({
                "Config": cfg,
                "Trace": trace_name,
                "Status": "Failed/Incomplete",
                "IPC": None,
                "L2C_Miss": None,
                "L2C_MPKI": None,
                "PF_Issued": None,
                "PF_Useful": None,
                "PF_Useless": None,
                "PF_Accuracy": None,
                "DRAM_Traffic": None
            })
            continue

        instructions = int(sim_match.group(1))
        ipc = float(sim_match.group(2))

        # Extract L2C demand misses by removing prefetch misses from total L2C misses
        l2_total_match = re.search(
            r"cpu0_L2C TOTAL\s+ACCESS:\s+\d+\s+HIT:\s+\d+\s+MISS:\s+(\d+)",
            content,
        )
        l2_pf_match = re.search(
            r"cpu0_L2C PREFETCH\s+ACCESS:\s+\d+\s+HIT:\s+\d+\s+MISS:\s+(\d+)",
            content,
        )

        if l2_total_match:
            total_miss = int(l2_total_match.group(1))
            pf_miss = int(l2_pf_match.group(1)) if l2_pf_match else 0
            l2c_miss = total_miss - pf_miss
        else:
            l2c_miss = None

        # Calculate MPKI
        mpki = (l2c_miss / (instructions / 1000.0)) if l2c_miss is not None else None

        # Extract Prefetch Stats: Accuracy = Useful / Prefetch Fill (Useful + Useless)
        pf_match = re.search(
            r"cpu0_L2C PREFETCH REQUESTED:\s+\d+\s+ISSUED:\s+(\d+)\s+USEFUL:\s+(\d+)\s+USELESS:\s+(\d+)",
            content
        )
        pf_issued = int(pf_match.group(1)) if pf_match else 0
        pf_useful = int(pf_match.group(2)) if pf_match else 0
        pf_useless = int(pf_match.group(3)) if pf_match else 0
        pf_fill = pf_useful + pf_useless
        accuracy = (pf_useful / pf_fill) if pf_fill > 0 else 0.0

        # Extract DRAM traffic from row-buffer hits and misses
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
            "PF_Useless": pf_useless,
            "PF_Accuracy": round(accuracy * 100, 2),
            "DRAM_Traffic": total_dram
        })

df = pd.DataFrame(results)
df.to_csv("simulation_summary.csv", index=False)
print(df.to_string())
print("\nResults successfully saved to simulation_summary.csv")