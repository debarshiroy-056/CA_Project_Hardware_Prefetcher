import os
import re
import glob
import pandas as pd

prefetchers = {
    "Baseline": "results_baseline", 
    "AMPM": "results_ampm", 
    "IP-Stride": "results_stride", 
    "FDP-Stride": "results_improved_stride", 
    "SPP": "results_spp", 
    "Berti": "results_berti", 
    "Pythia": "results_pythia"
}

traces = [
    "603.bwaves", "605.mcf", "619.lbm", 
    "620.omnetpp", "623.xalancbmk", "649.fotonik3d",
    "ligra_BFSCC", "ligra_PageRankDelta", "ligra_Triangle"
]

results = []

def parse_sim_file(filepath):
    data = {"IPC": None, "L2_Misses": None, "Useful_PF": 0, "PF_Fill": 0, "Mem_Traffic": 0, "Instr": 100000000}
    
    with open(filepath, 'r') as f:
        text = f.read()
        
        ipc_match = re.search(r"CPU 0 cumulative IPC:\s+([0-9.]+)", text)
        if ipc_match: data["IPC"] = float(ipc_match.group(1))
        
        l2_match = re.search(r"L2C TOTAL\s+ACCESS:\s+\d+\s+HIT:\s+\d+\s+MISS:\s+(\d+)", text)
        if l2_match: data["L2_Misses"] = float(l2_match.group(1))
            
        pf_match = re.search(r"L2C PREFETCH\s+REQUESTED:\s+\d+\s+ISSUED:\s+(\d+)\s+USEFUL:\s+(\d+)", text)
        if pf_match:
            data["PF_Fill"] = float(pf_match.group(1))
            data["Useful_PF"] = float(pf_match.group(2))
            
        # FIXED: Using LLC MISS as the 1:1 metric for Memory (DRAM) Traffic
        llc_match = re.search(r"LLC TOTAL\s+ACCESS:\s+\d+\s+HIT:\s+\d+\s+MISS:\s+(\d+)", text)
        if llc_match: data["Mem_Traffic"] = float(llc_match.group(1))
            
    return data

def find_file(folder, trace_base):
    if not os.path.exists(folder): return None
    matches = glob.glob(os.path.join(folder, f"*{trace_base}*.txt"))
    return matches[0] if matches else None

for trace in traces:
    trace_short = trace.replace("ligra_", "")
    base_filepath = find_file(prefetchers["Baseline"], trace)
    if not base_filepath: continue
        
    base_data = parse_sim_file(base_filepath)
    
    for pref, folder in prefetchers.items():
        filepath = find_file(folder, trace)
        if not filepath: continue
            
        data = parse_sim_file(filepath)
        if data["IPC"] is None: continue
            
        mpki = (base_data["L2_Misses"] / base_data["Instr"]) * 1000 if pref == "Baseline" else None
        coverage = (base_data["L2_Misses"] - data["L2_Misses"]) / base_data["L2_Misses"] if base_data["L2_Misses"] else 0
        accuracy = data["Useful_PF"] / data["PF_Fill"] if data["PF_Fill"] > 0 else 0
        speedup = data["IPC"] / base_data["IPC"]
        
        results.append({
            "Trace": trace_short,
            "Prefetcher": pref,
            "Baseline_L2C_MPKI": round(mpki, 4) if mpki else "-",
            "Coverage": round(coverage, 4) if pref != "Baseline" else "-",
            "Accuracy": round(accuracy, 4) if pref != "Baseline" else "-",
            "IPC_Speedup": round(speedup, 4),
            "Memory_Traffic": data["Mem_Traffic"]
        })

df = pd.DataFrame(results)
df.to_csv("endsem_evaluation_metrics.csv", index=False)
print("Data extracted successfully!")
