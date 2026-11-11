import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.lines import Line2D

from plot_style import PREFETCHER_COLORS, apply_publication_style, save_figure

PLOT_DIR = Path('plots')
PLOT_DIR.mkdir(exist_ok=True)
apply_publication_style()

# 1. Load and prepare data
df = pd.read_csv("endsem_evaluation_metrics.csv")
df['IPC_Speedup'] = pd.to_numeric(df['IPC_Speedup'], errors='coerce')

# Filter out baseline for the bars
pf_df = df[df['Prefetcher'] != 'Baseline'].copy()
ipc_pivot = pf_df.pivot(index='Trace', columns='Prefetcher', values='IPC_Speedup')

cols = ['AMPM', 'IP-Stride', 'FDP-Stride', 'SPP', 'Berti', 'Pythia']
ipc_pivot = ipc_pivot[cols].dropna(how='all')

# Sort by mean performance across all prefetchers so the plot is easy to read
ipc_pivot['mean'] = ipc_pivot.mean(axis=1)
ipc_pivot = ipc_pivot.sort_values('mean').drop(columns='mean')

# 2. Configure the plot
fig, ax = plt.subplots(figsize=(13, 9), layout='constrained')
y = np.arange(len(ipc_pivot))

# Adjust bar height and offsets for 6 prefetchers instead of 3
bar_height = 0.13
offsets = {p: (i - (len(cols) - 1) / 2) * bar_height for i, p in enumerate(cols)}

# 3. Draw the bars
for config in cols:
    values = ipc_pivot[config].to_numpy()
    bars = ax.barh(
        y + offsets[config], 
        values,
        height=bar_height, 
        color=PREFETCHER_COLORS[config], 
        edgecolor='black', 
        linewidth=0.5, 
        label=config
    )
    # Add the value annotations next to the bars
    for bar, value in zip(bars, values):
        if pd.notna(value):
            ax.annotate(
                f'{value:.3f}', 
                xy=(value, bar.get_y() + bar.get_height() / 2),
                xytext=(4, 0), 
                textcoords='offset points', 
                ha='left', 
                va='center', 
                fontsize=8
            )

# 4. Draw the Baseline and format the axes
max_val = ipc_pivot.max().max()
ax.set_xlim(0, max_val * 1.15) # Add 15% padding for the text labels
ax.axvline(1.0, color='red', linestyle='--', linewidth=1.2)

ax.set_yticks(y)
ax.set_yticklabels(ipc_pivot.index, fontsize=10)
ax.set_xlabel('IPC speedup relative to baseline', fontsize=13)
ax.set_title('IPC Speedup Relative to Baseline', fontsize=16, fontweight='bold', pad=12)

# 5. Recreate the custom legend matching your mid-semester style
handles, labels = ax.get_legend_handles_labels()
# Manually create a legend handle for the red dashed baseline
baseline_handle = Line2D([0], [0], color='red', linestyle='--', linewidth=1.2)

fig.legend(
    [baseline_handle] + handles,
    ['Baseline (1.0)'] + labels,
    title='Prefetcher',
    ncols=1,
    loc='center left',
    bbox_to_anchor=(1.02, 0.5),
    frameon=False,
    borderaxespad=0.0,
)

ax.grid(axis='x', linestyle='--', alpha=0.5)
ax.set_axisbelow(True)

# 6. Save using your publication style
save_figure(fig, PLOT_DIR / 'ipc_speedup.png')
print(f"Success: Saved clean plots/ipc_speedup.png")
