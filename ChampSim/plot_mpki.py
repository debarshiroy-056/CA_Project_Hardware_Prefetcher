import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

from plot_style import PREFETCHER_COLORS, apply_publication_style, save_figure

PLOT_DIR = Path('plots')
PLOT_DIR.mkdir(exist_ok=True)
apply_publication_style()

df = pd.read_csv("endsem_evaluation_metrics.csv")
# Only the baseline has MPKI recorded in the new CSV structure
baseline_df = df[df['Prefetcher'] == 'Baseline'].copy()
baseline_df['Baseline_L2C_MPKI'] = pd.to_numeric(baseline_df['Baseline_L2C_MPKI'], errors='coerce')

ax = baseline_df.set_index('Trace')[['Baseline_L2C_MPKI']].plot(
    kind='bar', figsize=(14, 8), edgecolor='white', linewidth=0.7, width=0.4, color='#666666', legend=False
)

plt.title('L2 Cache Demand Misses Per Kilo-Instruction (MPKI)', fontsize=16, fontweight='bold', pad=14)
plt.ylabel('L2C Demand MPKI')
plt.xlabel('Workload (Traces)')

for container in ax.containers:
    labels = [f'{v:.1f}' if pd.notna(v) and v > 0 else '' for v in container.datavalues]
    ax.bar_label(container, labels=labels, padding=3, fontsize=10, color='#222222')

plt.xticks(rotation=30, ha='right')
plt.grid(axis='y', linestyle=':', linewidth=0.8, alpha=0.7)
plt.gcf().set_layout_engine('constrained')

save_figure(plt.gcf(), PLOT_DIR / 'l2c_mpki.png')
print("Success: Saved plots/l2c_mpki.png")
