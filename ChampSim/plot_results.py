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
df = df[df['Status'] == 'Success'] # Filter out the crashed runs

# Pivot data to get Traces as rows and Configs as columns
ipc_df = df.pivot(index='Trace', columns='Config', values='IPC')

# Calculate Speedup (Prefetcher IPC / Baseline IPC)
speedup_df = pd.DataFrame(index=ipc_df.index)
for prefetcher in ['stride', 'spp', 'ampm']:
    if prefetcher in ipc_df.columns:
        speedup_df[prefetcher] = ipc_df[prefetcher] / ipc_df['baseline']

# Exclude traces without a complete baseline/prefetcher comparison.
speedup_df = speedup_df.dropna(how='all')

# Plotting the Speedup Chart
ax = speedup_df.plot(kind='bar', figsize=(14, 8), edgecolor='black', width=0.8)

plt.title('IPC Speedup Relative to Baseline Configuration', fontsize=16, fontweight='bold')
plt.ylabel('Speedup', fontsize=14)
plt.xlabel('Workload (Traces)', fontsize=14)

# Draw a red dashed line at 1.0 to show the baseline performance
baseline_line = plt.axhline(y=1.0, color='red', linestyle='--', label='Baseline (1.0)')

# Zoom in on the measured range because the differences are small.
y_min = speedup_df.min().min()
y_max = speedup_df.max().max()
ax.set_ylim(y_min - 0.005, y_max + 0.005)
ax.set_yticks(np.arange(np.floor((y_min - 0.005) * 100) / 100,
                        np.ceil((y_max + 0.005) * 100) / 100 + 0.001, 0.01))
ax.yaxis.set_major_formatter(plt.FormatStrFormatter('%.2f'))

for container in ax.containers:
    ax.bar_label(container, fmt='%.3f', padding=3, fontsize=9)

# Formatting tweaks
plt.xticks(rotation=35, ha='right', fontsize=10)
bar_handles = [container.patches[0] for container in ax.containers]
plt.legend(bar_handles + [baseline_line], ['Stride', 'SPP', 'AMPM', 'Baseline (1.0)'],
           title='Prefetcher')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

# Save the high-res image
output_path = PLOT_DIR / 'ipc_speedup.png'
plt.savefig(output_path, dpi=300)
print(f"Success: Saved {output_path}")
