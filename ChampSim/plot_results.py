import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from plot_style import PREFETCHER_COLORS, apply_publication_style, save_figure

# 1. Setup Directories and Academic Formatting
PLOT_DIR = Path('plots')
PLOT_DIR.mkdir(exist_ok=True)

apply_publication_style()

# 2. Load and Clean the Data
df = pd.read_csv("endsem_evaluation_metrics.csv")
# Convert the string hyphens '-' from the CSV into NaNs for plotting
df.replace('-', np.nan, inplace=True)

metrics = ['IPC_Speedup', 'Accuracy', 'Coverage', 'Memory_Traffic']
for col in metrics:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Filter out Baseline for relative metrics
df_prefs = df[df['Prefetcher'] != 'Baseline'].copy()

# Sort traces by Mean IPC Speedup so all plots share a consistent workload order
trace_order = df_prefs.groupby('Trace')['IPC_Speedup'].mean().sort_values().index.tolist()

# 3. Plotting Configuration
prefetchers = ['AMPM', 'IP-Stride', 'FDP-Stride', 'SPP', 'Berti', 'Pythia']
colors = PREFETCHER_COLORS
bar_height = 0.13
# Calculate precise vertical offsets for 6 bars to center them on the y-tick
offsets = {p: (i - (len(prefetchers) - 1) / 2) * bar_height for i, p in enumerate(prefetchers)}

# 4. Generalized Horizontal Bar Chart Generator
def generate_plot(metric_col, title, xlabel, filename, draw_baseline_at=None):
    # Pivot data specifically for this metric
    pivot_df = df_prefs.pivot(index='Trace', columns='Prefetcher', values=metric_col)
    pivot_df = pivot_df.reindex(trace_order) # Apply consistent sorting

    fig, ax = plt.subplots(figsize=(13, 8.5), layout='constrained')
    y = np.arange(len(pivot_df))

    # Track max value to set x-axis limits dynamically
    max_val = 0
    min_val = 0

    for config in prefetchers:
        if config not in pivot_df: continue
        values = pivot_df[config].to_numpy()

        # Update limits
        valid_vals = values[~np.isnan(values)]
        if len(valid_vals) > 0:
            max_val = max(max_val, valid_vals.max())
            min_val = min(min_val, valid_vals.min())

        bars = ax.barh(
            y + offsets[config],
            values,
            height=bar_height,
            color=colors[config],
            edgecolor='white',
            linewidth=0.7,
            label=config,
        )

        # Add value annotations next to the bars
        for bar, value in zip(bars, values):
            if pd.notna(value):
                # If negative (e.g. negative coverage), place label on the left
                ha_align = 'left' if value >= 0 else 'right'
                offset_pts = (4, 0) if value >= 0 else (-4, 0)

                ax.annotate(
                    f'{value:.3f}',
                    xy=(value, bar.get_y() + bar.get_height() / 2),
                    xytext=offset_pts,
                    textcoords='offset points',
                    ha=ha_align,
                    va='center',
                    fontsize=8.5,
                    color='#222222',
                )

    # Styling and Limits
    padding = (max_val - min_val) * 0.15 if max_val != min_val else 0.1
    ax.set_xlim(min(0, min_val - padding), max_val + padding)

    if draw_baseline_at is not None:
        ax.axvline(draw_baseline_at, color='#333333', linestyle='--', linewidth=1.3,
                   label=f'Baseline ({draw_baseline_at})')

    ax.set_yticks(y)
    ax.set_yticklabels(pivot_df.index, fontsize=10.5)
    ax.set_xlabel(xlabel)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=14)
    ax.legend(title='Prefetcher', ncols=1, loc='center left',
              bbox_to_anchor=(1.02, 0.5), frameon=False, borderaxespad=0.0)
    ax.grid(axis='x', linestyle=':', linewidth=0.8, alpha=0.7)
    ax.set_axisbelow(True)

    output_path = PLOT_DIR / filename
    save_figure(fig, output_path)
    print(f"Success: Saved {output_path}")

# 5. Generate All TA Required Plots
print("Generating End-Semester Plots...")
generate_plot('IPC_Speedup', 'IPC Speedup Relative to Baseline', 'IPC Speedup', '1_ipc_speedup.png', draw_baseline_at=1.0)
generate_plot('Accuracy', 'Prefetcher Accuracy', 'Accuracy Ratio (Useful / Issued)', '2_accuracy.png', draw_baseline_at=None)
generate_plot('Coverage', 'Demand Miss Coverage', 'Coverage Ratio', '3_coverage.png', draw_baseline_at=0.0)
generate_plot('Memory_Traffic', 'Total Memory Traffic', 'DRAM Requests', '4_memory_traffic.png', draw_baseline_at=None)

print("\nAll plots generated perfectly! You can find them in the 'plots' folder.")
