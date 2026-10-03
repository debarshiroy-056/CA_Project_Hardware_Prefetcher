import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import re

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

def short_trace_name(trace):
    name = re.sub(r'\.champsimtrace(?:\.xz|\.gz)?$', '', trace)
    name = re.sub(r'\.com-lj\.ungraph\.gcc_6\.3\.0_O3\.drop_\d+M\.length_\d+M$', '', name)
    return re.sub(r'_s-\d+B$', '', name)

speedup_df.index = [short_trace_name(trace) for trace in speedup_df.index]
speedup_df['mean'] = speedup_df.mean(axis=1)
speedup_df = speedup_df.sort_values('mean').drop(columns='mean')

# Plot speedup horizontally so every workload label remains readable.
fig, ax = plt.subplots(figsize=(12, 7))
y = range(len(speedup_df))
bar_height = 0.24
colors = {'stride': '#377eb8', 'spp': '#ff7f00', 'ampm': '#4daf4a'}
labels = {'stride': 'Stride', 'spp': 'SPP', 'ampm': 'AMPM'}
offsets = {'stride': -bar_height, 'spp': 0, 'ampm': bar_height}

for config in ['stride', 'spp', 'ampm']:
    if config not in speedup_df:
        continue
    values = speedup_df[config].to_numpy()
    bars = ax.barh(
        [value + offsets[config] for value in y],
        values,
        height=bar_height,
        color=colors[config],
        edgecolor='black',
        linewidth=0.5,
        label=labels[config],
    )
    for bar, value in zip(bars, values):
        if pd.notna(value):
            ax.annotate(
                f'{value:.3f}',
                xy=(value, bar.get_y() + bar.get_height() / 2),
                xytext=(4, 0),
                textcoords='offset points',
                ha='left',
                va='center',
                fontsize=9,
            )

max_speedup = speedup_df.max().max()
ax.set_xlim(0, max_speedup * 1.12)
ax.axvline(1.0, color='red', linestyle='--', linewidth=1.2, label='Baseline (1.0)')
ax.set_yticks(list(y))
ax.set_yticklabels(speedup_df.index, fontsize=10)
ax.set_xlabel('IPC speedup relative to baseline', fontsize=13)
ax.set_title('IPC Speedup Relative to Baseline', fontsize=16, fontweight='bold', pad=12)
ax.legend(title='Prefetcher', ncols=4, loc='lower center',
          bbox_to_anchor=(0.5, 1.14), frameon=False)
ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.set_axisbelow(True)
fig.subplots_adjust(top=0.72)

# Save the high-res image
output_path = PLOT_DIR / 'ipc_speedup.png'
fig.savefig(output_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"Success: Saved {output_path}")
