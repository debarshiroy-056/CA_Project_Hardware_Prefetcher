from pathlib import Path
import matplotlib.pyplot as plt

PREFETCHER_COLORS = {
    'AMPM': '#4daf4a',
    'IP-Stride': '#377eb8',
    'FDP-Stride': '#e41a1c',
    'SPP': '#ff7f00',
    'Berti': '#984ea3',
    'Pythia': '#a65628'
}

def apply_publication_style():
    plt.rcParams.update({
        'font.family': 'serif',
        'font.serif': ['Times New Roman'],
        'font.size': 11,
        'axes.titlesize': 16,
        'axes.titleweight': 'bold',
        'axes.labelsize': 13,
        'axes.labelpad': 8,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'legend.title_fontsize': 11,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.linewidth': 0.8,
        'grid.color': '#B0B0B0',
        'grid.linestyle': '--',
        'grid.linewidth': 0.7,
        'grid.alpha': 0.45,
        'savefig.dpi': 600,
        'savefig.facecolor': 'white',
        'figure.facecolor': 'white',
    })

def save_figure(fig, output_path: Path):
    fig.savefig(output_path, dpi=600, bbox_inches='tight', pad_inches=0.12)
    plt.close(fig)
