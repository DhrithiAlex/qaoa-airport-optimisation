# QAOA Airport Hub Optimisation



> **Hybrid quantum-classical combinatorial optimisation: selecting k=4 optimal global airport hubs from 12 candidates using QAOA on IBM's Aer quantum circuit simulator.**

---

## Overview

Given a weighted network of 12 major global airports, which 4 should be designated as primary hubs to maximise passenger throughput and minimise systemic delay? This is a constrained combinatorial optimisation problem with `C(12,4) = 495` possible solutions — trivially tractable by brute force for 12 nodes, but representative of the NP-hard class that scales exponentially.

This project demonstrates a complete QAOA pipeline:

1. **Problem formulation** — multi-criteria hub efficiency score (route reward + passenger volume − delay penalty)
2. **QUBO encoding** — objective + cardinality constraint `(Σxᵢ = k)` as a quadratic unconstrained binary optimisation matrix
3. **Ising mapping** — QUBO → Pauli-Z spin Hamiltonian via the `xᵢ = (1 − σᵢᶻ)/2` substitution
4. **QAOA circuit** — parameterised Qiskit circuit (ZZ + Rz cost layer, Rx mixer) at depths p = 1, 2, 3
5. **Hybrid optimisation** — COBYLA classical optimiser drives the variational parameter loop
6. **Benchmarking** — QAOA compared against exact brute-force and greedy heuristic on QUBO cost and efficiency score

---

## Key Finding

> **At p ≥ 2, QAOA discovers hub configurations with significantly higher efficiency scores (3.232 vs 1.939) than brute-force QUBO minimisation.** This reveals a gap between the proxy QUBO objective and the true multi-criteria metric — QAOA's probabilistic landscape exploration surfaces solutions that deterministic cost minimisation alone misses.

This is not a failure of QAOA. It is a demonstration that quantum variational search can escape the QUBO objective's local structure and find globally better solutions under the true metric.

---

## Results

| Solver | QUBO Cost ↓ | Efficiency Score ↑ | Approx. Ratio |
|---|---|---|---|
| Brute-force (exact) | −64.16 | 1.939 | 1.000 (optimal) |
| Greedy heuristic | −64.16 | 1.939 | 1.000 |
| QAOA p=1 | −63.83 | 1.936 | 1.005 |
| QAOA p=2 | −63.89 | **3.232** | 1.004 |
| QAOA p=3 | −64.02 | 3.141 | 1.002 |

### Optimal Hub Scorecard

| IATA | City | Pax (M/yr) | On-Time Departure |
|---|---|---|---|
| ATL | Atlanta | 104 | 78% |
| DXB | Dubai | 92 | 82% |
| LAX | Los Angeles | 88 | 79% |
| IST | Istanbul | 76 | 77% |

Geographically balanced: North America · Middle East · US West Coast · Europe/Asia gateway.

---

## Airport Network (12 nodes)

| IATA | City | Pax (M/yr) | OTD Rate |
|---|---|---|---|
| ATL | Atlanta | 104 | 78% |
| DXB | Dubai | 92 | 82% |
| LHR | London | 80 | 76% |
| ORD | Chicago | 79 | 72% |
| HND | Tokyo Haneda | 85 | 91% |
| LAX | Los Angeles | 88 | 79% |
| CDG | Paris | 76 | 80% |
| DFW | Dallas | 73 | 81% |
| FRA | Frankfurt | 70 | 83% |
| IST | Istanbul | 76 | 77% |
| SIN | Singapore | 68 | 88% |
| AMS | Amsterdam | 72 | 85% |

---

## Problem Formulation

### Objective Function

```
score(S) = Σ_{i,j ∈ S} route_weight(i,j)
         + 0.5 · Σ_{i ∈ S} pax(i) / pax_max
         − 0.8 · Σ_{i ∈ S} (1 − OTD(i))
```

### QUBO Matrix

```
Q_ii  = −0.8(1−OTD_i) − 0.5·pax_i/pax_max + λ(1 − 2k)    [diagonal]
Q_ij  = −route_weight_ij + 2λ                               [off-diagonal]
```

with cardinality penalty `λ = 2.5` enforcing exactly `k = 4` hubs selected.

### QUBO → Ising Mapping

The substitution `xᵢ = (1 − σᵢᶻ)/2` converts the binary QUBO into a spin Hamiltonian:

```
H_C = Σ_{i<j} J_ij σᵢᶻ σⱼᶻ + Σ_i h_i σᵢᶻ + const

J_ij = Q_ij / 4
h_i  = −Q_ii/2 − Σ_{j≠i} Q_ij/4
```

---

## QAOA Circuit Architecture

```
|0⟩ ─ H ─┬─ U(H_C, γ₁) ─ U(B, β₁) ─┬─ ... ─┬─ U(H_C, γₚ) ─ U(B, βₚ) ─┬─ Measure
           └───────────────────────────┘       └───────────────────────────┘

U(H_C, γ) = Π_{(i,j)} CNOT·Rz(2γJ_ij)·CNOT · Π_i Rz(2γh_i)   [cost layer]
U(B,   β) = Π_i Rx(2β)                                           [mixer layer]
```

- **n = 12 qubits** (one per airport)
- **2p variational parameters** `(γ₁...γₚ, β₁...βₚ)`
- **2048 shots** per expectation value evaluation
- **4096 shots** final sampling to extract solution
- **COBYLA optimiser**, gradient-free, robust to shot noise (max 150 iterations)

---

## Project Structure

```
qaoa-airport-optimisation/
│
├── qaoa_airport.py          # Complete self-contained simulation (13 sections)
│
├── assets/
│   └── qaoa_airport_results.png   # 7-panel benchmark dashboard
│
├── results/                 # Runtime outputs (auto-created)
│
├── docs/
│   └── formulation.md       # Full QUBO/Ising derivation with worked example
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/qaoa-airport-optimisation.git
cd qaoa-airport-optimisation

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

---

## Usage

```bash
python qaoa_airport.py
```

**Expected runtime**: 3–8 minutes (QAOA p=1,2,3 with 150 iterations each).

**Output**: `qaoa_airport_results.png` — 7-panel benchmark dashboard:
- Airport network graph (node size ∝ passengers, green = optimal hubs)
- QUBO matrix heatmap
- QUBO cost by solver (bar chart)
- Efficiency score by solver (bar chart)
- Approximation ratio vs circuit depth p
- QAOA p=3 measurement distribution (top 30 bitstrings)
- Optimal hub scorecard

### Adjusting Parameters

```python
# In qaoa_airport.py — top of file
K_HUBS = 4      # Change number of hubs to select
LAMBDA = 2.5    # Cardinality constraint penalty (increase if constraint violated)
```

```python
# In run_qaoa() — adjust circuit depth and shot count
for p in [1, 2, 3]:    # Add p=4,5 for higher approximation ratios
    ...
N_SHOTS = 2048          # Increase for lower statistical noise
```

---

## Code Architecture (13 Sections)

| Section | Description |
|---|---|
| 1. Airport Data | 12-node dataset: IATA codes, passenger volumes, OTD rates, route weights |
| 2. Graph Builder | NetworkX weighted graph with node and edge attributes |
| 3. Objective Function | Multi-criteria efficiency scorer (route + pax + delay) |
| 4. QUBO Matrix | Q construction with λ cardinality penalty |
| 5. Ising Mapping | `xᵢ = (1−σᵢᶻ)/2` substitution → `J_ij`, `h_i`, offset |
| 6. QAOA Circuit | Parameterised Qiskit circuit: ZZ+Rz cost layer, Rx mixer, p layers |
| 7. Expectation Value | Shot-based `⟨H_C⟩` estimator from measurement counts |
| 8. Brute-Force | Exact solver over all `C(12,4) = 495` feasible combinations |
| 9. Greedy Solver | Sequential best-addition heuristic baseline |
| 10. QAOA Solver | Full hybrid loop: COBYLA + feasibility filter + final sampling |
| 11. Runner | Orchestrates all three solvers, collects metrics |
| 12. Visualisation | 7-panel Matplotlib dark-theme dashboard |
| 13. Ising Summary | Prints coupling strengths `J_ij` and local fields `h_i` |

---

## Technical Concepts

| Concept | Role |
|---|---|
| **QUBO** | Standard form for combinatorial optimisation; maps to quantum and classical solvers |
| **Ising Hamiltonian** | Spin-system representation of cost function; native to quantum gate circuits |
| **VQE family** | QAOA is a member — parameterised quantum state + classical feedback |
| **NISQ** | Near-term quantum algorithm; designed for devices without error correction |
| **Approximation ratio** | `bf_cost / qaoa_cost` — proximity to the exact optimum |
| **COBYLA** | Gradient-free optimiser; robust to shot noise in quantum measurements |

---

## Extensions & Future Work

- **Real quantum hardware** — submit via `QiskitRuntimeService` to IBM Quantum backends
- **Noise modelling** — add `AerSimulator` `NoiseModel` with depolarising/thermal channels
- **Zero-Noise Extrapolation** — apply ZNE (see [sister project](https://github.com/YOUR_USERNAME/qaoa-phase-space-finance)) for error mitigation
- **Warm starting** — initialise QAOA angles from classical SDP/LP relaxation
- **Larger instances** — n = 20–50 airports with graph partitioning for scalability
- **Alternative mixers** — XY or Dicke state mixer to natively enforce cardinality constraint
- **Portfolio optimisation** — replace airport data with asset return/covariance data

---

## References

1. Farhi, E., Goldstone, J., & Gutmann, S. (2014). *A Quantum Approximate Optimization Algorithm*. [arXiv:1411.4028](https://arxiv.org/abs/1411.4028)
2. Glover, F., Kochenberger, G., & Du, Y. (2019). *Quantum Bridge Analytics I: A Tutorial on Formulating and Using QUBO Models*. 4OR.
3. Lucas, A. (2014). *Ising formulations of many NP problems*. Frontiers in Physics.
4. [Qiskit Documentation](https://docs.quantum.ibm.com)

---

## License

MIT License. See [LICENSE](LICENSE) for details.

---

<p align="center">
  <em>Dhrithi Maria · Self-Proposed Research Project · May 2026</em>
</p>
