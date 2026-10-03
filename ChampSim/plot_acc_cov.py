import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import re

PLOT_DIR = Path('plots')
PLOT_DIR.mkdir(exist_ok=True)

# Enforce academic formatting
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 12

df = pd.read_csv("simulation_summary.csv")
df = df[df['Status'] == 'Success']

# Extract baseline misses for the Coverage calculation
baseline_df = df[df['Config'] == 'baseline'][['Trace', 'L2C_Miss']].set_index('Trace')
baseline_misses = baseline_df['L2C_Miss']

# Filter out baseline for these plots (baseline doesn't issue prefetches)
pf_df = df[df['Config'].isin(['stride', 'spp', 'ampm'])].copy()

# Calculate Coverage: (Useful Prefetches / Baseline Demand Misses) * 100
# Calculate Coverage using the exact rubric formula:
# (Misses in no prefetch - Misses with prefetch) / Misses in no prefetch
def get_coverage(row):
    trace = row['Trace']
    if trace in baseline_misses.index and baseline_misses[trace] > 0 and pd.notna(row['L2C_Miss']):
        return ((baseline_misses[trace] - row['L2C_Miss']) / baseline_misses[trace]) * 100
    return float('nan')

pf_df['PF_Coverage'] = pf_df.apply(get_coverage, axis=1)

# Pivot data for plotting
acc_pivot = pf_df.pivot(index='Trace', columns='Config', values='PF_Accuracy')
cov_pivot = pf_df.pivot(index='Trace', columns='Config', values='PF_Coverage')

# Clean up empty columns
cols = ['stride', 'spp', 'ampm']
acc_pivot = acc_pivot[[c for c in cols if c in acc_pivot.columns]].dropna(how='all')
cov_pivot = cov_pivot[[c for c in cols if c in cov_pivot.columns]].dropna(how='all')

def short_trace_name(trace):
    name = re.sub(r'\.champsimtrace(?:\.xz|\.gz)?$', '', trace)
    name = re.sub(r'\.com-lj\.ungraph\.gcc_6\.3\.0_O3\.drop_\d+M\.length_\d+M$', '', name)
    return re.sub(r'_s-\d+B$', '', name)

# 1. Plot Accuracy as a horizontal grouped bar chart.
accuracy = acc_pivot.copy()
accuracy.index = [short_trace_name(trace) for trace in accuracy.index]
accuracy['mean'] = accuracy.mean(axis=1)
accuracy = accuracy.sort_values('mean').drop(columns='mean')

fig, ax1 = plt.subplots(figsize=(12, 7))
y = range(len(accuracy))
bar_height = 0.24
colors = {'stride': '#377eb8', 'spp': '#ff7f00', 'ampm': '#4daf4a'}
labels = {'stride': 'Stride', 'spp': 'SPP', 'ampm': 'AMPM'}
offsets = {'stride': -bar_height, 'spp': 0, 'ampm': bar_height}

for config in cols:
    if config not in accuracy:
        continue
    values = accuracy[config].to_numpy()
    bars = ax1.barh(
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
            ax1.annotate(
                f'{value:.1f}%',
                xy=(value, bar.get_y() + bar.get_height() / 2),
                xytext=(4, 0),
                textcoords='offset points',
                ha='left',
                va='center',
                fontsize=9,
            )

ax1.set_xlim(0, 108)
ax1.set_yticks(list(y))
ax1.set_yticklabels(accuracy.index, fontsize=10)
ax1.set_xlabel('Prefetch accuracy (%)', fontsize=13)
ax1.set_title('Prefetcher Accuracy by Workload', fontsize=16, fontweight='bold', pad=12)
ax1.legend(title='Prefetcher', ncols=3, loc='lower center',
           bbox_to_anchor=(0.5, 1.08), frameon=False)
ax1.grid(axis='x', linestyle='--', alpha=0.5)
ax1.set_axisbelow(True)
fig.subplots_adjust(top=0.78)
fig.savefig(PLOT_DIR / 'pf_accuracy.png', dpi=300, bbox_inches='tight')
plt.close(fig)

# 2. Plot Coverage as a horizontal diverging bar chart.
# Negative values mean the prefetcher caused more misses than the baseline.
coverage = cov_pivot.copy()
coverage['mean'] = coverage.mean(axis=1)
coverage = coverage.sort_values('mean').drop(columns='mean')

coverage.index = [short_trace_name(trace) for trace in coverage.index]

fig, ax2 = plt.subplots(figsize=(12, 7))
y = range(len(coverage))
bar_height = 0.24
colors = {'stride': '#377eb8', 'spp': '#ff7f00', 'ampm': '#4daf4a'}
labels = {'stride': 'Stride', 'spp': 'SPP', 'ampm': 'AMPM'}
offsets = {'stride': -bar_height, 'spp': 0, 'ampm': bar_height}

for config in cols:
    if config not in coverage:
        continue
    values = coverage[config].to_numpy()
    bars = ax2.barh(
        [value + offsets[config] for value in y],
        values,
        height=bar_height,
        color=colors[config],
        edgecolor='black',
        linewidth=0.5,
        label=labels[config],
    )
    for bar, value in zip(bars, values):
        if pd.isna(value):
            continue
        ax2.annotate(
            f'{value:.1f}%',
            xy=(value, bar.get_y() + bar.get_height() / 2),
            xytext=(4 if value >= 0 else -4, 0),
            textcoords='offset points',
            ha='left' if value >= 0 else 'right',
            va='center',
            fontsize=9,
        )

min_value = coverage.min().min()
max_value = coverage.max().max()
padding = max((max_value - min_value) * 0.10, 5)
ax2.set_xlim(min_value - padding, max_value + padding)
ax2.axvline(0, color='black', linewidth=1)
ax2.set_yticks(list(y))
ax2.set_yticklabels(coverage.index, fontsize=10)
ax2.set_xlabel('Coverage relative to baseline (%)', fontsize=13)
ax2.set_title('Prefetcher Coverage by Workload', fontsize=16, fontweight='bold', pad=12)
handles, legend_labels = ax2.get_legend_handles_labels()
fig.legend(
    handles,
    legend_labels,
    title='Prefetcher',
    ncols=3,
    loc='upper center',
    bbox_to_anchor=(0.5, 0.96),
    frameon=False,
)
ax2.grid(axis='x', linestyle='--', alpha=0.5)
ax2.set_axisbelow(True)
fig.text(
    0.5,
    0.015,
    'Positive = fewer L2 misses than baseline   |   Negative = more L2 misses than baseline',
    ha='center',
    fontsize=9,
    color='dimgray',
)

fig.subplots_adjust(top=0.82, bottom=0.10)
fig.savefig(PLOT_DIR / 'pf_coverage.png', dpi=300, bbox_inches='tight')
plt.close(fig)
print(f"Success: Saved {PLOT_DIR / 'pf_accuracy.png'} and {PLOT_DIR / 'pf_coverage.png'}")
