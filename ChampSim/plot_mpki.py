import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

PLOT_DIR = Path('plots')
PLOT_DIR.mkdir(exist_ok=True)

# Enforce Times New Roman for academic formatting
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 12

# Load and clean the data
df = pd.read_csv("simulation_summary.csv")
df = df[df['Status'] == 'Success'] 

# Pivot data to get Traces as rows and Configs as columns for MPKI
mpki_df = df.pivot(index='Trace', columns='Config', values='L2C_MPKI')
mpki_df = mpki_df.dropna(how='all')

# Reorder columns to ensure Baseline is compared against the prefetchers
cols = ['baseline', 'stride', 'spp', 'ampm']
mpki_df = mpki_df[[c for c in cols if c in mpki_df.columns]]

# Plotting the MPKI Chart
ax = mpki_df.plot(kind='bar', figsize=(14, 8), edgecolor='black', width=0.8)

plt.title('L2 Cache Misses Per Kilo-Instruction (MPKI)', fontsize=16, fontweight='bold')
plt.ylabel('L2C MPKI', fontsize=14)
plt.xlabel('Workload (Traces)', fontsize=14)

# Format the bars with values
for container in ax.containers:
    ax.bar_label(container, fmt='%.1f', padding=3, fontsize=9)

# Formatting tweaks
plt.xticks(rotation=35, ha='right', fontsize=10)
plt.legend(title='Configuration', labels=['Baseline', 'Stride', 'SPP', 'AMPM'])
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Save the high-res image
output_path = PLOT_DIR / 'l2c_mpki.png'
plt.savefig(output_path, dpi=300)
print(f"Success: Saved {output_path}")
