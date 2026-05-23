# QAOA for Airport Hub Optimization

**Solving the Optimal Hub Selection Problem using Quantum Approximate Optimization Algorithm (QAOA)**

![QAOA Airport Results](figures/qaoa_airport_results.png)

## Overview

This project tackles a real-world combinatorial optimization problem:  
**Selecting the best k airports to serve as hubs** in a global network to maximize throughput while minimizing delays.

The problem is formulated as a **QUBO** (Quadratic Unconstrained Binary Optimization) with a cardinality constraint, then solved using:
- **Brute Force** (exact)
- **Greedy Heuristic**
- **QAOA** (p=1, 2, 3 layers) on Qiskit Aer simulator

## Features

- Realistic 12-airport dataset with passenger traffic and on-time performance
- QUBO formulation with soft cardinality constraint
- Ising model conversion
- QAOA circuit construction with parameterized layers
- Classical benchmarks + approximation ratio analysis
- Rich multi-panel visualization (network graph, QUBO heatmap, performance comparison, etc.)

## Installation

```bash
git clone https://github.com/DhrithiAlex/qaoa-airport-optimisation.git
cd qaoa-airport-optimisation

pip install -e .
