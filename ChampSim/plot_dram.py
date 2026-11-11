import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

from plot_style import PREFETCHER_COLORS, apply_publication_style, save_figure

PLOT_DIR = Path('plots')
PLOT_DIR.mkdir(exist_ok=True)
apply_publication_style()

df = pd.read_csv("endsem_evaluation_metrics.csv")
df['Memory_Traffic'] = pd.to_numeric(df['Memory_Traffic'], errors='coerce')

# Pivot data
dram_df = df.pivot(index='Trace', columns='Prefetcher', values='Memory_Traffic')

cols = ['AMPM', 'IP-Stride', 'FDP-Stride', 'SPP', 'Berti', 'Pythia']
baseline_dram = dram_df['Baseline'].replace(0, np.nan) # Prevent division by zero

norm_dram_df = pd.DataFrame(index=dram_df.index)
for prefetcher in cols:
    norm_dram_df[prefetcher] = dram_df[prefetcher] / baseline_dram

# If all values are NaN (meaning LLC misses weren't recorded), skip plotting empty bars
if norm_dram_df.isna().all().all():
    print("Warning: Memory_Traffic contains no non-zero baseline values to normalize against.")
else:
    ax = norm_dram_df[cols].plot(
        kind='bar', figsize=(14, 8), edgecolor='white', linewidth=0.7, width=0.85,
        color=[PREFETCHER_COLORS[c] for c in cols],
    )
    plt.title('DRAM Traffic Overhead (Normalized to Baseline)', fontsize=16, fontweight='bold', pad=14)
    plt.ylabel('Normalized DRAM Traffic')
    plt.xlabel('Workload (Traces)')
    baseline_line = plt.axhline(y=1.0, color='#333333', linestyle='--', linewidth=1.3, label='Baseline (1.0)')

    y_max = norm_dram_df.max().max()
    ax.set_ylim(0, max(1.1, y_max * 1.15))

    for container in ax.containers:
        labels = [f'{v:.2f}' if pd.notna(v) else '' for v in container.datavalues]
        ax.bar_label(container, labels=labels, padding=3, fontsize=8, color='#222222', rotation=90)

    plt.xticks(rotation=35, ha='right')
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(handles + [baseline_line], labels + ['Baseline (1.0)'], title='Configuration', ncols=3)
    plt.grid(axis='y', linestyle=':', linewidth=0.8, alpha=0.7)
    plt.gcf().set_layout_engine('constrained')

    save_figure(plt.gcf(), PLOT_DIR / 'dram_traffic.png')
    print(f"Success: Saved {PLOT_DIR / 'dram_traffic.png'}")
