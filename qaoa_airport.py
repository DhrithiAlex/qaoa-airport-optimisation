"""
QAOA for Airport Efficiency Optimization
=========================================
Problem: Given a weighted airport network, find the subset of k airports
that maximises global throughput while minimising systemic delay —
the "optimal hub set" problem.

Formulation
-----------
  QUBO:  min  xᵀ Q x
         Q_ij = –w_ij (route traffic reward)  i ≠ j
         Q_ii = d_i   (delay penalty)
         + λ · (Σxᵢ – k)²  (cardinality constraint: choose exactly k hubs)

  Ising: xᵢ = (1 – σᵢᶻ) / 2   →   H_C spin Hamiltonian
         Variational state: |γ,β⟩ = e^{-iβ_p B} e^{-iγ_p H_C} … |+⟩

Benchmarks
----------
  · Brute-force  (exact, feasible for n ≤ 20)
  · Greedy       (classic heuristic)
  · QAOA         (p = 1, 2, 3 layers — approximation ratio reported)
"""

import itertools, warnings, time
import numpy as np
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

from scipy.optimize import minimize

from qiskit import QuantumCircuit
from qiskit.circuit import Parameter, ParameterVector
from qiskit_aer import AerSimulator

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# 1.  AIRPORT DATA  (realistic subset — 12 major global hubs)
# ─────────────────────────────────────────────────────────────

AIRPORTS = {
    0:  {"name": "ATL", "city": "Atlanta",       "pax_M": 104, "otd": 0.78},
    1:  {"name": "DXB", "city": "Dubai",         "pax_M":  92, "otd": 0.82},
    2:  {"name": "LHR", "city": "London",        "pax_M":  80, "otd": 0.76},
    3:  {"name": "ORD", "city": "Chicago",       "pax_M":  79, "otd": 0.72},
    4:  {"name": "HND", "city": "Tokyo Haneda",  "pax_M":  85, "otd": 0.91},
    5:  {"name": "LAX", "city": "Los Angeles",   "pax_M":  88, "otd": 0.79},
    6:  {"name": "CDG", "city": "Paris",         "pax_M":  76, "otd": 0.80},
    7:  {"name": "DFW", "city": "Dallas",        "pax_M":  73, "otd": 0.81},
    8:  {"name": "FRA", "city": "Frankfurt",     "pax_M":  70, "otd": 0.83},
    9:  {"name": "IST", "city": "Istanbul",      "pax_M":  76, "otd": 0.77},
    10: {"name": "SIN", "city": "Singapore",     "pax_M":  68, "otd": 0.88},
    11: {"name": "AMS", "city": "Amsterdam",     "pax_M":  72, "otd": 0.85},
}
N_AIRPORTS = len(AIRPORTS)

# Route connectivity matrix — normalised bidirectional traffic weight
ROUTES = {
    (0,3):0.92,(0,5):0.88,(0,7):0.85,(0,2):0.70,(0,6):0.65,
    (1,10):0.80,(1,2):0.75,(1,6):0.72,(1,8):0.70,(1,11):0.68,
    (2,6):0.90,(2,8):0.85,(2,11):0.82,(2,3):0.68,(2,5):0.65,
    (3,7):0.88,(3,5):0.82,(3,9):0.62,(3,4):0.60,
    (4,10):0.85,(4,1):0.78,(4,5):0.75,(4,8):0.65,
    (5,7):0.86,(5,10):0.72,(5,6):0.68,
    (6,8):0.88,(6,11):0.84,(6,9):0.70,
    (7,9):0.65,(7,8):0.70,
    (8,11):0.88,(8,9):0.72,
    (9,11):0.68,(9,10):0.62,
    (10,11):0.74,
}
# Symmetrise
for (i,j),w in list(ROUTES.items()):
    ROUTES[(j,i)] = w

K_HUBS = 4          # Select this many optimal hubs
LAMBDA  = 2.5       # Cardinality constraint penalty weight


# ─────────────────────────────────────────────────────────────
# 2.  BUILD WEIGHTED GRAPH
# ─────────────────────────────────────────────────────────────

def build_graph():
    G = nx.Graph()
    for i, info in AIRPORTS.items():
        G.add_node(i, **info)
    for (i,j),w in ROUTES.items():
        if i < j:
            G.add_edge(i, j, weight=w)
    return G

G = build_graph()


# ─────────────────────────────────────────────────────────────
# 3.  OBJECTIVE FUNCTION  (classical evaluation)
# ─────────────────────────────────────────────────────────────

def efficiency_score(subset):
    """
    Score a hub subset. Higher = better.
    = Σ route_weights within subset
    + Σ pax_normalised for selected airports
    – Σ delay_penalty for selected airports
    """
    subset = list(subset)
    route_reward = sum(
        ROUTES.get((i,j), 0.0)
        for i in subset for j in subset if i < j
    )
    pax_max   = max(a["pax_M"] for a in AIRPORTS.values())
    pax_bonus = sum(AIRPORTS[i]["pax_M"]/pax_max for i in subset)
    delay_pen = sum(1.0 - AIRPORTS[i]["otd"] for i in subset)
    return route_reward + 0.5*pax_bonus - 0.8*delay_pen


# ─────────────────────────────────────────────────────────────
# 4.  QUBO MATRIX
# ─────────────────────────────────────────────────────────────

def build_qubo():
    """
    Minimise –score(x) + λ(Σxᵢ – k)²
    Q_ii  = delay_i – pax_i/pax_max·0.5  +  λ(1 – 2k)
    Q_ij  = –route_weight_ij             +  2λ          (i≠j)
    """
    Q = np.zeros((N_AIRPORTS, N_AIRPORTS))
    pax_max = max(a["pax_M"] for a in AIRPORTS.values())

    for i in range(N_AIRPORTS):
        d_i  = -(1.0 - AIRPORTS[i]["otd"])*0.8
        p_i  =  AIRPORTS[i]["pax_M"]/pax_max * 0.5
        Q[i,i] = d_i - p_i + LAMBDA*(1 - 2*K_HUBS)

    for (i,j),w in ROUTES.items():
        if i < j:
            Q[i,j] += -w + 2*LAMBDA
            Q[j,i] = Q[i,j]

    return Q


# ─────────────────────────────────────────────────────────────
# 5.  QUBO → ISING  (diagonal Jᵢⱼ and hᵢ)
# ─────────────────────────────────────────────────────────────

def qubo_to_ising(Q):
    """
    xᵢ = (1 – σᵢᶻ)/2
    H_C = Σᵢⱼ Jᵢⱼ σᵢᶻ σⱼᶻ + Σᵢ hᵢ σᵢᶻ + const
    """
    n = Q.shape[0]
    J = np.zeros((n,n))
    h = np.zeros(n)
    offset = 0.0

    for i in range(n):
        for j in range(i+1, n):
            J[i,j] = Q[i,j] / 4.0

    for i in range(n):
        h[i] = -Q[i,i]/2.0 - sum(Q[i,j]/4.0 for j in range(n) if j!=i)
        offset += Q[i,i]/2.0

    for i in range(n):
        for j in range(i+1,n):
            offset += Q[i,j]/4.0

    return J, h, offset


# ─────────────────────────────────────────────────────────────
# 6.  QAOA CIRCUIT
# ─────────────────────────────────────────────────────────────

def build_qaoa_circuit(J, h, p):
    """
    Build QAOA circuit with p layers.
    Returns (circuit, gamma_params, beta_params)
    """
    n = J.shape[0]
    gamma = ParameterVector("γ", p)
    beta  = ParameterVector("β", p)
    qc    = QuantumCircuit(n)

    # |+⟩ initial state
    qc.h(range(n))

    for layer in range(p):
        # ── Problem unitary U(H_C, γ) ──
        # ZZ couplings
        for i in range(n):
            for j in range(i+1, n):
                if abs(J[i,j]) > 1e-10:
                    qc.cx(i, j)
                    qc.rz(2 * gamma[layer] * J[i,j], j)
                    qc.cx(i, j)
        # Z biases
        for i in range(n):
            if abs(h[i]) > 1e-10:
                qc.rz(2 * gamma[layer] * h[i], i)

        # ── Mixer unitary U(B, β) ──
        for i in range(n):
            qc.rx(2 * beta[layer], i)

    qc.measure_all()
    return qc, gamma, beta


# ─────────────────────────────────────────────────────────────
# 7.  EXPECTATION VALUE  (sampled)
# ─────────────────────────────────────────────────────────────

backend = AerSimulator()
Q_MAT = build_qubo()
J_MAT, H_VEC, OFFSET = qubo_to_ising(Q_MAT)

def qubo_cost(bitstring):
    x = np.array([int(b) for b in bitstring])
    return float(x @ Q_MAT @ x)

def expectation(params, qc, gamma_params, beta_params, p, shots=2048):
    gamma_vals = params[:p]
    beta_vals  = params[p:]
    bind_dict  = {gamma_params[i]: gamma_vals[i] for i in range(p)}
    bind_dict.update({beta_params[i]: beta_vals[i] for i in range(p)})

    bound_qc = qc.assign_parameters(bind_dict)
    job      = backend.run(bound_qc, shots=shots)
    counts   = job.result().get_counts()

    exp_val = 0.0
    total   = sum(counts.values())
    for bitstring, count in counts.items():
        exp_val += (count/total) * qubo_cost(bitstring)
    return exp_val


# ─────────────────────────────────────────────────────────────
# 8.  BRUTE-FORCE SOLVER  (exact, feasible for n ≤ 20)
# ─────────────────────────────────────────────────────────────

def brute_force():
    t0 = time.time()
    best_cost, best_subset = float("inf"), None
    for combo in itertools.combinations(range(N_AIRPORTS), K_HUBS):
        x = np.zeros(N_AIRPORTS)
        x[list(combo)] = 1.0
        cost = float(x @ Q_MAT @ x)
        if cost < best_cost:
            best_cost, best_subset = cost, list(combo)
    return best_subset, best_cost, time.time()-t0


# ─────────────────────────────────────────────────────────────
# 9.  GREEDY SOLVER
# ─────────────────────────────────────────────────────────────

def greedy():
    t0 = time.time()
    selected, remaining = [], list(range(N_AIRPORTS))
    for _ in range(K_HUBS):
        best_gain, best_node = float("inf"), None
        for node in remaining:
            candidate = selected + [node]
            x = np.zeros(N_AIRPORTS); x[candidate] = 1.0
            cost = float(x @ Q_MAT @ x)
            if cost < best_gain:
                best_gain, best_node = cost, node
        selected.append(best_node)
        remaining.remove(best_node)
    x = np.zeros(N_AIRPORTS); x[selected] = 1.0
    return selected, float(x @ Q_MAT @ x), time.time()-t0


# ─────────────────────────────────────────────────────────────
# 10.  QAOA SOLVER
# ─────────────────────────────────────────────────────────────

def run_qaoa(p, shots=2048):
    t0 = time.time()
    qc, gamma_params, beta_params = build_qaoa_circuit(J_MAT, H_VEC, p)

    # Random initial guess
    rng = np.random.default_rng(42)
    x0  = rng.uniform(0, 2*np.pi, 2*p)

    result = minimize(
        expectation,
        x0,
        args=(qc, gamma_params, beta_params, p, shots),
        method="COBYLA",
        options={"maxiter": 150, "rhobeg": 1.0},
    )

    # Sample from optimised circuit
    gamma_opt = result.x[:p]
    beta_opt  = result.x[p:]
    bind_dict = {gamma_params[i]: gamma_opt[i] for i in range(p)}
    bind_dict.update({beta_params[i]: beta_opt[i] for i in range(p)})
    bound_qc  = qc.assign_parameters(bind_dict)

    job    = backend.run(bound_qc, shots=4096)
    counts = job.result().get_counts()

    # Pick lowest-cost feasible bitstring (exactly k ones)
    best_cost, best_bs = float("inf"), None
    for bs, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        if bs.count("1") == K_HUBS:
            c = qubo_cost(bs)
            if c < best_cost:
                best_cost, best_bs = c, bs

    # Fallback: best k from any bitstring
    if best_bs is None:
        best_bs = min(counts, key=lambda b: qubo_cost(b))
        best_cost = qubo_cost(best_bs)

    subset = [i for i,b in enumerate(reversed(best_bs)) if b == "1"][:K_HUBS]
    elapsed = time.time()-t0

    # Collect optimisation landscape
    landscape = []
    for bs, cnt in counts.items():
        if bs.count("1") == K_HUBS:
            landscape.append((qubo_cost(bs), cnt))

    return subset, best_cost, elapsed, result, counts, landscape


# ─────────────────────────────────────────────────────────────
# 11.  RUN EVERYTHING
# ─────────────────────────────────────────────────────────────

print("="*60)
print("  QAOA AIRPORT EFFICIENCY OPTIMIZER")
print(f"  {N_AIRPORTS} airports  ·  k={K_HUBS} hubs  ·  λ={LAMBDA}")
print("="*60)

print("\n[1/3] Brute-force (exact)…")
bf_subset, bf_cost, bf_time = brute_force()
bf_score = efficiency_score(bf_subset)
print(f"  Hubs: {[AIRPORTS[i]['name'] for i in bf_subset]}")
print(f"  QUBO cost: {bf_cost:.4f}  |  Efficiency score: {bf_score:.4f}  |  {bf_time:.2f}s")

print("\n[2/3] Greedy heuristic…")
gr_subset, gr_cost, gr_time = greedy()
gr_score = efficiency_score(gr_subset)
print(f"  Hubs: {[AIRPORTS[i]['name'] for i in gr_subset]}")
print(f"  QUBO cost: {gr_cost:.4f}  |  Efficiency score: {gr_score:.4f}  |  {gr_time:.2f}s")

print("\n[3/3] QAOA (p=1, p=2, p=3)…")
qaoa_results = {}
for p in [1, 2, 3]:
    print(f"  Running p={p}…", end=" ", flush=True)
    subset, cost, elapsed, opt_res, counts, landscape = run_qaoa(p)
    score = efficiency_score(subset)
    approx_ratio = bf_cost / cost if cost != 0 else 0   # < 1 means QAOA is worse
    qaoa_results[p] = dict(
        subset=subset, cost=cost, score=score, elapsed=elapsed,
        opt_res=opt_res, counts=counts, landscape=landscape,
        approx_ratio=approx_ratio
    )
    print(f"hubs={[AIRPORTS[i]['name'] for i in subset]}  cost={cost:.4f}  score={score:.4f}  "
          f"approx_ratio={approx_ratio:.3f}  {elapsed:.1f}s")


# ─────────────────────────────────────────────────────────────
# 12.  VISUALISATION  (5-panel figure)
# ─────────────────────────────────────────────────────────────

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

plt.savefig("/mnt/user-data/outputs/qaoa_airport_results.png",
            dpi=150, bbox_inches="tight", facecolor=BG)
print("[Figure saved → qaoa_airport_results.png]")


# ─────────────────────────────────────────────────────────────
# 13.  PRINT ISING HAMILTONIAN SUMMARY
# ─────────────────────────────────────────────────────────────

print("\n" + "="*60)
print("  ISING HAMILTONIAN SUMMARY")
print("="*60)
print(f"\n  H_C = Σᵢⱼ Jᵢⱼ σᵢᶻσⱼᶻ + Σᵢ hᵢ σᵢᶻ + {OFFSET:.4f}")
print(f"\n  Non-zero J couplings (top 5 by magnitude):")
J_flat = [(abs(J_MAT[i,j]), i, j, J_MAT[i,j])
          for i in range(N_AIRPORTS) for j in range(i+1, N_AIRPORTS)
          if abs(J_MAT[i,j]) > 1e-6]
for _, i, j, v in sorted(J_flat, reverse=True)[:5]:
    print(f"    J[{AIRPORTS[i]['name']},{AIRPORTS[j]['name']}] = {v:+.4f}")

print(f"\n  Local fields hᵢ (all airports):")
for i in range(N_AIRPORTS):
    bar = "█" * int(abs(H_VEC[i])*8)
    print(f"    h[{AIRPORTS[i]['name']:3s}] = {H_VEC[i]:+.4f}  {bar}")

print("\n" + "="*60)
print("  BENCHMARK SUMMARY")
print("="*60)
print(f"  {'Solver':<18} {'Hubs':<24} {'Cost':>8}  {'Score':>7}  {'Time':>6}  {'Approx ratio':>12}")
print(f"  {'-'*18} {'-'*24} {'-'*8}  {'-'*7}  {'-'*6}  {'-'*12}")

hubs_str = ",".join(AIRPORTS[i]["name"] for i in bf_subset)
print(f"  {'Brute-force':<18} {hubs_str:<24} {bf_cost:>8.4f}  {bf_score:>7.4f}  {bf_time:>5.2f}s  {'1.000 (optimal)':>12}")

hubs_str = ",".join(AIRPORTS[i]["name"] for i in gr_subset)
ratio = bf_cost/gr_cost if gr_cost != 0 else 0
print(f"  {'Greedy':<18} {hubs_str:<24} {gr_cost:>8.4f}  {gr_score:>7.4f}  {gr_time:>5.2f}s  {ratio:>12.3f}")

for p in [1,2,3]:
    r = qaoa_results[p]
    hubs_str = ",".join(AIRPORTS[i]["name"] for i in r["subset"])
    print(f"  {f'QAOA p={p}':<18} {hubs_str:<24} {r['cost']:>8.4f}  {r['score']:>7.4f}  {r['elapsed']:>5.1f}s  {r['approx_ratio']:>12.3f}")

print("\n  Done.")
