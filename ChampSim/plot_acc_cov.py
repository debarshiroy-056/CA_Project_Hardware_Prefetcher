import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

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
def get_coverage(row):
    trace = row['Trace']
    if trace in baseline_misses.index and baseline_misses[trace] > 0:
        return (row['PF_Useful'] / baseline_misses[trace]) * 100
    return 0.0

pf_df['PF_Coverage'] = pf_df.apply(get_coverage, axis=1)

# Pivot data for plotting
acc_pivot = pf_df.pivot(index='Trace', columns='Config', values='PF_Accuracy')
cov_pivot = pf_df.pivot(index='Trace', columns='Config', values='PF_Coverage')

# Clean up empty columns
cols = ['stride', 'spp', 'ampm']
acc_pivot = acc_pivot[[c for c in cols if c in acc_pivot.columns]].dropna(how='all')
cov_pivot = cov_pivot[[c for c in cols if c in cov_pivot.columns]].dropna(how='all')

# 1. Plot Accuracy
ax1 = acc_pivot.plot(kind='bar', figsize=(14, 6), edgecolor='black', width=0.7)
plt.title('Prefetcher Accuracy (%)', fontsize=16, fontweight='bold')
plt.ylabel('Accuracy (%)', fontsize=14)
plt.xlabel('Workload (Traces)', fontsize=14)
plt.xticks(rotation=35, ha='right', fontsize=10)
plt.legend(title='Prefetcher', labels=['Stride', 'SPP', 'AMPM'])
plt.grid(axis='y', linestyle='--', alpha=0.7)

for container in ax1.containers:
    ax1.bar_label(container, fmt='%.1f', padding=3, fontsize=9)

plt.tight_layout()
plt.savefig(PLOT_DIR / 'pf_accuracy.png', dpi=300)
plt.close()

# 2. Plot Coverage
ax2 = cov_pivot.plot(kind='bar', figsize=(14, 6), edgecolor='black', width=0.7)
plt.title('Prefetcher Coverage (%)', fontsize=16, fontweight='bold')
plt.ylabel('Coverage (%)', fontsize=14)
plt.xlabel('Workload (Traces)', fontsize=14)
plt.xticks(rotation=35, ha='right', fontsize=10)
plt.legend(title='Prefetcher', labels=['Stride', 'SPP', 'AMPM'])
plt.grid(axis='y', linestyle='--', alpha=0.7)

for container in ax2.containers:
    ax2.bar_label(container, fmt='%.1f', padding=3, fontsize=9)

plt.tight_layout()
plt.savefig(PLOT_DIR / 'pf_coverage.png', dpi=300)
print(f"Success: Saved {PLOT_DIR / 'pf_accuracy.png'} and {PLOT_DIR / 'pf_coverage.png'}")
