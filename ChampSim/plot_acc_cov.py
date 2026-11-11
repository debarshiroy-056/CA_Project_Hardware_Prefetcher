import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

from plot_style import PREFETCHER_COLORS, apply_publication_style, save_figure

PLOT_DIR = Path('plots')
PLOT_DIR.mkdir(exist_ok=True)
apply_publication_style()

df = pd.read_csv("endsem_evaluation_metrics.csv")
df.replace('-', np.nan, inplace=True)
for col in ['Coverage', 'Accuracy']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

pf_df = df[df['Prefetcher'] != 'Baseline'].copy()
# Convert Accuracy to percentage for consistency with your mid-sem plot
pf_df['PF_Accuracy'] = pf_df['Accuracy'] * 100
# The new CSV already calculates coverage as a ratio, convert to percentage
pf_df['PF_Coverage'] = pf_df['Coverage'] * 100

acc_pivot = pf_df.pivot(index='Trace', columns='Prefetcher', values='PF_Accuracy')
cov_pivot = pf_df.pivot(index='Trace', columns='Prefetcher', values='PF_Coverage')

cols = ['AMPM', 'IP-Stride', 'FDP-Stride', 'SPP', 'Berti', 'Pythia']
acc_pivot = acc_pivot[cols].dropna(how='all')
cov_pivot = cov_pivot[cols].dropna(how='all')

# 1. Plot Accuracy
accuracy = acc_pivot.copy()
accuracy['mean'] = accuracy.mean(axis=1)
accuracy = accuracy.sort_values('mean').drop(columns='mean')

fig, ax1 = plt.subplots(figsize=(13, 9), layout='constrained')
y = range(len(accuracy))
bar_height = 0.13
offsets = {p: (i - (len(cols) - 1) / 2) * bar_height for i, p in enumerate(cols)}

for config in cols:
    values = accuracy[config].to_numpy()
    bars = ax1.barh(
        [value + offsets[config] for value in y], values,
        height=bar_height, color=PREFETCHER_COLORS[config], edgecolor='white', linewidth=0.7, label=config
    )
    for bar, value in zip(bars, values):
        if pd.notna(value):
            ax1.annotate(f'{value:.1f}%', xy=(value, bar.get_y() + bar.get_height() / 2),
                         xytext=(4, 0), textcoords='offset points', ha='left', va='center', fontsize=8)

ax1.set_xlim(0, 108)
ax1.set_yticks(list(y))
ax1.set_yticklabels(accuracy.index, fontsize=10)
ax1.set_xlabel('Prefetch accuracy (%)')
ax1.set_title('Prefetcher Accuracy by Workload', fontsize=16, fontweight='bold', pad=12)
ax1.legend(title='Prefetcher', ncols=1, loc='center left',
           bbox_to_anchor=(1.02, 0.5), frameon=False, borderaxespad=0.0)
ax1.grid(axis='x', linestyle=':', linewidth=0.8, alpha=0.7)
ax1.set_axisbelow(True)
save_figure(fig, PLOT_DIR / 'pf_accuracy.png')

# 2. Plot Coverage
coverage = cov_pivot.copy()
coverage = coverage.reindex(accuracy.index) # Keep consistent trace ordering

fig, ax2 = plt.subplots(figsize=(13, 9), layout='constrained')
for config in cols:
    values = coverage[config].to_numpy()
    bars = ax2.barh(
        [value + offsets[config] for value in y], values,
        height=bar_height, color=PREFETCHER_COLORS[config], edgecolor='white', linewidth=0.7, label=config
    )
    for bar, value in zip(bars, values):
        if pd.notna(value):
            ax2.annotate(f'{value:.1f}%', xy=(value, bar.get_y() + bar.get_height() / 2),
                         xytext=(4 if value >= 0 else -4, 0), textcoords='offset points',
                         ha='left' if value >= 0 else 'right', va='center', fontsize=8)

min_val, max_val = coverage.min().min(), coverage.max().max()
ax2.set_xlim(min_val * 1.15 if min_val < 0 else 0, max_val * 1.15)
ax2.axvline(0, color='#333333', linewidth=1.2)
ax2.set_yticks(list(y))
ax2.set_yticklabels(coverage.index, fontsize=10)
ax2.set_xlabel('Coverage relative to baseline (%)')
ax2.set_title('Prefetcher Coverage by Workload', fontsize=16, fontweight='bold', pad=12)
ax2.legend(title='Prefetcher', ncols=1, loc='center left',
           bbox_to_anchor=(1.02, 0.5), frameon=False, borderaxespad=0.0)
ax2.grid(axis='x', linestyle=':', linewidth=0.8, alpha=0.7)
save_figure(fig, PLOT_DIR / 'pf_coverage.png')
print(f"Success: Saved {PLOT_DIR / 'pf_accuracy.png'} and {PLOT_DIR / 'pf_coverage.png'}")
