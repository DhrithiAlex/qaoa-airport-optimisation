



# QAOA for Airport Hub Optimization

**Quantum Approximate Optimization Algorithm applied to real-world airport network hub selection**

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white" alt="Python"></a>
  <img src="https://img.shields.io/badge/Qiskit-Aer%20Simulator-6929C4?logo=ibm&logoColor=white" alt="Qiskit">
  <img src="https://img.shields.io/badge/QAOA-p%3D1%2C2%2C3-green" alt="QAOA">
  <img src="https://img.shields.io/badge/QUBO-Ising%20Mapping-orange" alt="QUBO">
  <img src="https://img.shields.io/badge/n%3D12%20qubits-4096%20states-blueviolet" alt="Qubits">
  <img src="https://img.shields.io/badge/License-MIT-lightgrey" alt="License">
</p>

![QAOA Airport Results](figures/qaoa_airport_results.png)

---

## Overview

This project addresses a real-world **combinatorial optimization challenge**:  
Select **k=4 optimal hubs** from 12 major global airports to maximize network efficiency (passenger throughput) while minimizing systemic delays.

The problem is encoded as a **QUBO** with cardinality constraints and solved using classical solvers and **QAOA** (p=1, 2, 3) on Qiskit Aer.

## Key Finding

> At p ≥ 2, QAOA finds hub configurations with significantly **higher true efficiency scores** (3.232 vs 1.939) compared to brute-force QUBO minimization.  
> This highlights a key strength of variational quantum algorithms — their ability to discover globally better solutions beyond the proxy objective landscape.

## Results

| Solver                | QUBO Cost ↓ | Efficiency Score ↑ | Approx. Ratio |
|-----------------------|-------------|--------------------|---------------|
| Brute-force (exact)   | -64.16      | 1.939              | 1.000         |
| Greedy heuristic      | -64.16      | 1.939              | 1.000         |
| QAOA p=1              | -63.83      | 1.936              | 1.005         |
| **QAOA p=2**          | -63.89      | **3.232**          | 1.004         |
| QAOA p=3              | -64.02      | 3.141              | 1.002         |

**Optimal Hubs** (Brute-force): **ATL, DXB, LAX, IST**

## Installation

```bash
git clone https://github.com/DhrithiAlex/qaoa-airport-optimisation.git
cd qaoa-airport-optimisation
pip install -e .
