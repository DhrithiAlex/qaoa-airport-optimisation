import numpy as np
from .data import AIRPORTS, G, K_HUBS
from .classical_solvers import brute_force, greedy
from .qaoa import run_qaoa  # You will need to implement run_qaoa in qaoa.py or here
from .visualization import plot_results

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
#   PRINT ISING HAMILTONIAN SUMMARY
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

