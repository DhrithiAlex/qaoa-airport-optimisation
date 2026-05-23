# QAOA for Airport Hub Optimization





<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white" alt="Python"></a>
  <img src="https://img.shields.io/badge/Qiskit-Aer%20Simulator-6929C4?logo=ibm&logoColor=white" alt="Qiskit">
  <img src="https://img.shields.io/badge/QAOA-p%3D1%2C2%2C3-green" alt="QAOA">
  <img src="https://img.shields.io/badge/QUBO-Ising%20Mapping-orange" alt="QUBO">
  <img src="https://img.shields.io/badge/n%3D12%20qubits-4096%20states-blueviolet" alt="Qubits">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="License">
</p>

> **Hybrid quantum-classical combinatorial optimisation: selecting k=4 optimal global airport hubs from 12 candidates using QAOA on IBM's Aer quantum circuit simulator.**
![QAOA Airport Results](figures/qaoa_airport_results.png)

---

## Overview
Given a weighted network of 12 major global airports, this project solves the problem of selecting **k=4 optimal hubs** to maximize passenger throughput while minimizing systemic delays.

The problem is formulated as a **QUBO** with cardinality constraints and solved using classical benchmarks and **QAOA** (p=1, 2, 3) on Qiskit Aer.

## Key Finding

> At p ≥ 2, QAOA discovers hub configurations with significantly higher efficiency scores (3.232 vs 1.939) than brute-force QUBO minimisation. This demonstrates how quantum variational methods can escape local structures of the proxy objective and find globally better solutions under the true multi-criteria metric.

## Results

| Solver              | QUBO Cost ↓ | Efficiency Score ↑ | Approx. Ratio |
|---------------------|-------------|--------------------|---------------|
| Brute-force (exact) | -64.16      | 1.939              | 1.000         |
| Greedy heuristic    | -64.16      | 1.939              | 1.000         |
| QAOA p=1            | -63.83      | 1.936              | 1.005         |
| QAOA p=2            | -63.89      | **3.232**          | 1.004         |
| QAOA p=3            | -64.02      | 3.141              | 1.002         |

**Optimal Hubs** (Brute-force): ATL, DXB, LAX, IST
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

## Installation

```bash
git clone https://github.com/DhrithiAlex/qaoa-airport-optimisation.git
cd qaoa-airport-optimisation
pip install -e .
