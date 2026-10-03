import sys
import pandas as pd
from collections import Counter

fname = sys.argv[1] if len(sys.argv) > 1 else "l2_demand_sample.csv"
df = pd.read_csv(fname)
df['CL_Int'] = df['CacheLineAddr'].apply(lambda x: int(str(x), 16))
df['Page'] = df['CL_Int'].apply(lambda x: x // 64)      # 4KB page = 64 cache lines
df['Offset'] = df['CL_Int'].apply(lambda x: x % 64)     # Offset within 4KB page (0..63)

print(f"\n=======================================================")
print(f" MEMORY ACCESS CHARACTERIZATION: {fname}")
print(f"=======================================================")
print(f"Total Sampled L2 Demand Accesses: {len(df)} | L2 Misses: {len(df[df['Hit']==0])}")

print("\n--- A. PC-LOCAL DELTA BEHAVIOR (Top 5 Load PCs by L2 Misses) ---")
misses_df = df[df['Hit'] == 0]
top_pcs = misses_df['LoadPC'].value_counts().head(5).index

for pc in top_pcs:
    pc_df = df[df['LoadPC'] == pc]
    l2_misses = len(pc_df[pc_df['Hit'] == 0])
    cl_list = pc_df['CL_Int'].tolist()
    deltas = [cl_list[i] - cl_list[i-1] for i in range(1, len(cl_list))]
    if len(deltas) > 0:
        most_freq_delta, count = Counter(deltas).most_common(1)[0]
        frac = (count / len(deltas)) * 100
    else:
        most_freq_delta, frac = 0, 0.0
    print(f"Load PC: {pc:<12} | L2 Misses: {l2_misses:<5} | Dominant Delta: {most_freq_delta:+8d} | Dominant Fraction: {frac:5.1f}%")

print("\n--- B. ORDERED DELTA HISTORY (Top Recurring 4-Delta Sequences) ---")
all_cl = df['CL_Int'].tolist()
global_deltas = [all_cl[i] - all_cl[i-1] for i in range(1, len(all_cl))]
page_deltas = [d for d in global_deltas if -63 <= d <= 63 and d != 0]
ngrams = [tuple(page_deltas[i:i+4]) for i in range(len(page_deltas)-3)]
for seq, count in Counter(ngrams).most_common(5):
    print(f"Delta Sequence {str(seq):<25} : {count} occurrences")

print("\n--- C. SPATIAL FOOTPRINTS (Across 4-KB Pages) ---")
page_groups = df.groupby('Page')['Offset'].unique()
footprints = [tuple(sorted(offsets)) for offsets in page_groups if len(offsets) >= 4]
unique_pages = len(page_groups)
avg_lines_per_page = df.groupby('Page')['Offset'].nunique().mean()
print(f"Total 4-KB Pages Touched: {unique_pages} | Avg Unique Cache Lines per Page: {avg_lines_per_page:.2f} / 64 ({avg_lines_per_page/64*100:.1f}% density)")
for fp, count in Counter(footprints).most_common(3):
    preview = str(list(fp[:8]))[:-1] + (", ...]" if len(fp) > 8 else "]")
    print(f"Recurring Page Offset Footprint {preview:<38} (len={len(fp):2d}/64) : {count} pages")
