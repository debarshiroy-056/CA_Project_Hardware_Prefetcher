import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

PLOT_DIR = Path('plots')
PLOT_DIR.mkdir(exist_ok=True)

# Enforce academic formatting
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 12

df = pd.read_csv("simulation_summary.csv")
df = df[df['Status'] == 'Success']

# Pivot data to get Traces as rows and Configs as columns
dram_df = df.pivot(index='Trace', columns='Config', values='DRAM_Traffic')

# A normalized comparison is meaningful only when a workload has a valid
# baseline and at least one prefetcher result.
prefetchers = ['stride', 'spp', 'ampm']
available_prefetchers = [c for c in prefetchers if c in dram_df.columns]
dram_df = dram_df.dropna(subset=['baseline'], how='any')
dram_df = dram_df[dram_df['baseline'] > 0]
dram_df = dram_df.dropna(subset=available_prefetchers, how='any')

baseline_dram = dram_df['baseline']
dram_df[available_prefetchers] = dram_df[available_prefetchers].replace(0, np.nan)
dram_df = dram_df.dropna(subset=available_prefetchers, how='any')

norm_dram_df = pd.DataFrame(index=dram_df.index)
plot_cols = available_prefetchers
for prefetcher in plot_cols:
    norm_dram_df[prefetcher] = dram_df[prefetcher] / baseline_dram

# Keep only workloads with at least one available normalized result.
norm_dram_df = norm_dram_df.dropna(how='all')
norm_dram_df.index = [trace.split('.')[0] for trace in norm_dram_df.index]

y_label = 'Normalized DRAM Traffic (Relative to Baseline)'

# Plotting
ax = norm_dram_df[plot_cols].plot(
    kind='bar', figsize=(14, 8), edgecolor='black', width=0.8
)

plt.title('DRAM Traffic Overhead', fontsize=16, fontweight='bold')
plt.ylabel(y_label, fontsize=14)
plt.xlabel('Workload (Traces)', fontsize=14)

# Draw a red dashed line at 1.0 to show the baseline.
baseline_line = plt.axhline(y=1.0, color='red', linestyle='--', label='Baseline (1.0)')

# Dynamically set y-axis limits 
y_max = norm_dram_df.max().max()
if pd.isna(y_max) or y_max == 0:
    y_max = 1.0
ax.set_ylim(0, max(1.1, y_max * 1.15))

for container in ax.containers:
    ax.bar_label(container, fmt='%.2f', padding=3, fontsize=9)

# Formatting tweaks
plt.xticks(rotation=35, ha='right', fontsize=10)
bar_handles = [container.patches[0] for container in ax.containers]
plt.legend(bar_handles + [baseline_line], ['Stride', 'SPP', 'AMPM', 'Baseline (1.0)'],
           title='Configuration')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Save the high-res image
plt.savefig(PLOT_DIR / 'dram_traffic.png', dpi=300)
print(f"Success: Saved {PLOT_DIR / 'dram_traffic.png'}")
