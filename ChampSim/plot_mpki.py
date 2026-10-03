import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PLOT_DIR = Path('plots')
PLOT_DIR.mkdir(exist_ok=True)

plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = ['Times New Roman']
plt.rcParams['font.size'] = 12

df = pd.read_csv("simulation_summary.csv")
df = df[df['Status'] == 'Success']

mpki_df = df.pivot(index='Trace', columns='Config', values='L2C_MPKI')

# Keep only workloads where baseline succeeded so comparisons are valid
cols = ['baseline', 'stride', 'spp', 'ampm']
mpki_df = mpki_df[[c for c in cols if c in mpki_df.columns]]
mpki_df = mpki_df.dropna(subset=['baseline'])

# Shorten trace names to match the other plots
def clean_name(t):
    if t.startswith('ligra_'):
        return t.split('.')[0]
    if t.startswith('llama2'):
        return 'llama2.c-stories15M.1'
    return t.split('_')[0]

mpki_df.index = [clean_name(t) for t in mpki_df.index]

ax = mpki_df.plot(kind='bar', figsize=(14, 7), edgecolor='black', width=0.8)

plt.title('L2 Cache Demand Misses Per Kilo-Instruction (MPKI)', fontsize=16, fontweight='bold')
plt.ylabel('L2C Demand MPKI', fontsize=14)
plt.xlabel('Workload (Traces)', fontsize=14)

for container in ax.containers:
    labels = [f'{v:.1f}' if pd.notna(v) and v > 0 else '' for v in container.datavalues]
    ax.bar_label(container, labels=labels, padding=3, fontsize=9)

plt.xticks(rotation=30, ha='right', fontsize=11)
plt.legend(['Baseline', 'Stride', 'SPP', 'AMPM'], title='Configuration')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()

plt.savefig(PLOT_DIR / 'l2c_mpki.png', dpi=300)
print("Success: Saved clean plots/l2c_mpki.png")