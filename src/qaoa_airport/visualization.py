import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import networkx as nx
from .data import AIRPORTS, G, K_HUBS

print("\n[Generating figures…]")
fig = plt.figure(figsize=(18, 13), facecolor="#0d1117")
gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.52, wspace=0.38)

ACCENT = "#58a6ff"
GREEN  = "#3fb950"
AMBER  = "#d29922"
RED    = "#f85149"
GRAY   = "#8b949e"
BG     = "#0d1117"
PANEL  = "#161b22"
BORDER = "#30363d"

def panel_ax(ax, title):
    ax.set_facecolor(PANEL)
    ax.tick_params(colors=GRAY, labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
    ax.set_title(title, color="#e6edf3", fontsize=10, pad=8)

# ── Panel 1: Airport graph ──────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
panel_ax(ax1, "Global airport network  (node size ∝ passengers, edge weight ∝ traffic)")

pos = nx.spring_layout(G, seed=7, k=1.6)
node_sizes = [AIRPORTS[n]["pax_M"]*12 for n in G.nodes()]
node_colors = []
best_hubs = set(bf_subset)
for n in G.nodes():
    node_colors.append(GREEN if n in best_hubs else ACCENT)

edges = list(G.edges(data=True))
edge_weights = [d["weight"] for _,_,d in edges]
nx.draw_networkx_edges(G, pos, ax=ax1,
    edge_color=[plt.cm.Blues(0.3 + 0.6*w) for w in edge_weights],
    width=[1.5*w for w in edge_weights], alpha=0.6)
nx.draw_networkx_nodes(G, pos, ax=ax1,
    node_size=node_sizes, node_color=node_colors, alpha=0.9)
nx.draw_networkx_labels(G, pos, ax=ax1,
    labels={i: AIRPORTS[i]["name"] for i in G.nodes()},
    font_size=7, font_color="#e6edf3")
ax1.set_axis_off()
ax1.text(0.01, 0.02, f"● Optimal hubs (brute-force k={K_HUBS})", transform=ax1.transAxes,
         color=GREEN, fontsize=8)

# ── Panel 2: QUBO heatmap ───────────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
panel_ax(ax2, "QUBO matrix  Q")
Q_display = Q_MAT.copy()
vmax = np.percentile(np.abs(Q_display), 95)
im = ax2.imshow(Q_display, cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
ax2.set_xticks(range(N_AIRPORTS))
ax2.set_yticks(range(N_AIRPORTS))
ax2.set_xticklabels([AIRPORTS[i]["name"] for i in range(N_AIRPORTS)],
                    rotation=90, fontsize=6, color=GRAY)
ax2.set_yticklabels([AIRPORTS[i]["name"] for i in range(N_AIRPORTS)],
                    fontsize=6, color=GRAY)
plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04).ax.yaxis.set_tick_params(color=GRAY, labelcolor=GRAY)

# ── Panel 3: Cost comparison bar ────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
panel_ax(ax3, "QUBO cost by solver")
labels = ["Brute\nforce", "Greedy"] + [f"QAOA\np={p}" for p in [1,2,3]]
costs  = [bf_cost, gr_cost] + [qaoa_results[p]["cost"] for p in [1,2,3]]
colors = [GREEN, AMBER] + [ACCENT]*3
bars   = ax3.bar(labels, costs, color=colors, width=0.55, edgecolor=BORDER, linewidth=0.5)
ax3.set_ylabel("QUBO cost (lower = better)", color=GRAY, fontsize=8)
ax3.axhline(bf_cost, color=GREEN, linestyle="--", linewidth=0.8, alpha=0.6)
for bar, cost in zip(bars, costs):
    ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.02,
             f"{cost:.2f}", ha="center", va="bottom", fontsize=7, color="#e6edf3")

# ── Panel 4: Efficiency score comparison ────────────────────
ax4 = fig.add_subplot(gs[1, 1])
panel_ax(ax4, "Efficiency score by solver")
scores = [bf_score, gr_score] + [qaoa_results[p]["score"] for p in [1,2,3]]
bars2  = ax4.bar(labels, scores, color=colors, width=0.55, edgecolor=BORDER, linewidth=0.5)
ax4.set_ylabel("Efficiency score (higher = better)", color=GRAY, fontsize=8)
ax4.axhline(bf_score, color=GREEN, linestyle="--", linewidth=0.8, alpha=0.6)
for bar, sc in zip(bars2, scores):
    ax4.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.001,
             f"{sc:.3f}", ha="center", va="bottom", fontsize=7, color="#e6edf3")

# ── Panel 5: Approximation ratio vs p ───────────────────────
ax5 = fig.add_subplot(gs[1, 2])
panel_ax(ax5, "QAOA approximation ratio vs depth p")
ps    = [1,2,3]
ratios= [qaoa_results[p]["approx_ratio"] for p in ps]
ax5.plot(ps, ratios, "o-", color=ACCENT, linewidth=2, markersize=8, markerfacecolor=ACCENT)
ax5.axhline(1.0, color=GREEN, linestyle="--", linewidth=1, label="Optimal (=1.0)")
ax5.set_xlabel("Circuit depth p", color=GRAY, fontsize=8)
ax5.set_ylabel("Approx ratio (closer to 1 = better)", color=GRAY, fontsize=8)
ax5.set_xticks(ps)
ax5.set_ylim(0, 1.15)
ax5.legend(fontsize=7, facecolor=PANEL, edgecolor=BORDER, labelcolor=GRAY)
for p, r in zip(ps, ratios):
    ax5.annotate(f"{r:.3f}", (p, r), textcoords="offset points", xytext=(0,8),
                 ha="center", fontsize=8, color="#e6edf3")

# ── Panel 6: QAOA measurement distribution (p=3) ─────────────
ax6 = fig.add_subplot(gs[2, :2])
panel_ax(ax6, f"QAOA p=3 measurement distribution (top 30 bitstrings, k={K_HUBS})")
counts_p3 = qaoa_results[3]["counts"]
sorted_counts = sorted(counts_p3.items(), key=lambda x: -x[1])[:30]
bs_labels = [bs for bs, _ in sorted_counts]
bs_values = [cnt for _, cnt in sorted_counts]
bar_colors = []
for bs in bs_labels:
    idx = [i for i,b in enumerate(reversed(bs)) if b=="1"][:K_HUBS]
    bar_colors.append(GREEN if set(idx) == best_hubs else ACCENT)
ax6.bar(range(len(bs_labels)), bs_values, color=bar_colors, edgecolor=BORDER, linewidth=0.3)
ax6.set_xticks(range(len(bs_labels)))
ax6.set_xticklabels(bs_labels, rotation=90, fontsize=5, color=GRAY)
ax6.set_ylabel("Counts", color=GRAY, fontsize=8)
ax6.text(0.99, 0.96, "● Optimal hub bitstring", transform=ax6.transAxes,
         color=GREEN, fontsize=8, ha="right", va="top")

# ── Panel 7: Optimised hub scorecard ────────────────────────
ax7 = fig.add_subplot(gs[2, 2])
ax7.set_facecolor(PANEL)
ax7.set_axis_off()
ax7.set_title("Optimal hub scorecard", color="#e6edf3", fontsize=10, pad=8)

hub_data = [(AIRPORTS[i]["name"], AIRPORTS[i]["city"],
             AIRPORTS[i]["pax_M"], AIRPORTS[i]["otd"])
            for i in sorted(bf_subset)]
col_labels = ["Code", "City", "Pax (M)", "OTD"]
table_data = [[a,b,f"{c}",f"{d:.0%}"] for a,b,c,d in hub_data]
t = ax7.table(cellText=table_data, colLabels=col_labels,
              cellLoc="center", loc="center", bbox=[0, 0.15, 1, 0.75])
t.auto_set_font_size(False); t.set_fontsize(8)
for (r,c), cell in t.get_celld().items():
    cell.set_facecolor(PANEL if r > 0 else "#1f2937")
    cell.set_edgecolor(BORDER)
    cell.set_text_props(color="#e6edf3" if r > 0 else ACCENT)

ax7.text(0.5, 0.05,
    f"Efficiency score: {bf_score:.4f}\nQUBO cost: {bf_cost:.4f}",
    transform=ax7.transAxes, ha="center", fontsize=8, color=GRAY)

# Title
fig.text(0.5, 0.97,
    "QAOA vs Classical Benchmarks — Global Airport Hub Optimisation",
    ha="center", fontsize=14, color="#e6edf3", fontweight="bold")
fig.text(0.5, 0.945,
    f"{N_AIRPORTS} airports  ·  k={K_HUBS} optimal hubs  ·  QUBO+Ising+QAOA  ·  Aer simulator",
    ha="center", fontsize=9, color=GRAY)

plt.savefig("/content/qaoa_airport_results.png",
            dpi=150, bbox_inches="tight", facecolor=BG)
print("[Figure saved → qaoa_airport_results.png]")
