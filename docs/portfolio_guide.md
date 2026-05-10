# Quantum Computing Portfolio — GitHub Setup Guide
## Dhrithi Maria | Two-Repository Strategy

---

## Your Two Repositories

| # | Repo Name | Framework | Core Concept | Visual |
|---|---|---|---|---|
| 1 | `qaoa-phase-space-finance` | PennyLane | Wigner-function ZNE + silver futures routing | Full analysis + Wigner profiling |
| 2 | `qaoa-airport-optimisation` | Qiskit Aer | QUBO/Ising QAOA + airport hub selection | 7-panel benchmark dashboard |

**Pin both on your GitHub profile.** Together they demonstrate two different quantum stacks (Qiskit + PennyLane), two different problem domains (finance + aviation), and two different algorithmic angles (noise mitigation + problem formulation). No recruiter will see this combination and think "tutorial project."

---

## Repository 1 — qaoa-phase-space-finance

### Description (GitHub About, 160 chars)
```
QAOA financial routing with Wigner-function noise calibration. Bridges CV quantum optics & NISQ computing via Zero-Noise Extrapolation. Silver futures Max-Cut.
```

### Topics
```
quantum-computing  qaoa  zero-noise-extrapolation  wigner-function
pennylane  nisq  noise-mitigation  quantum-finance  max-cut
optimization  python  quantum-optics  financial-routing
variational-quantum-eigensolver  combinatorial-optimization
```

### Git Commands (Windows VS Code terminal)

```bash
cd path\to\qaoa-phase-space-finance

git init
git branch -M main
git add .
git commit -m "Initial commit: Phase-Space Noise Calibration for QAOA Financial Optimization

- PennyLane QAOA circuit engine: ideal / noisy / ZNE-mitigated modes
- Wigner-function noise profiling for NISQ hardware characterization
- Richardson ZNE extrapolation with Wigner-derived scale factors
- Silver futures execution routing as weighted Max-Cut (6 venues)
- 30x30 energy landscape scan over (gamma, beta) parameter space
- COBYLA optimizer with 5 random restarts per regime
- Publication-quality composite figures (dark theme)
- Full thesis analogy map: CV quantum optics -> QAOA finance"

git remote add origin https://github.com/YOUR_USERNAME/qaoa-phase-space-finance.git
git push -u origin main
```

---

## Repository 2 — qaoa-airport-optimisation

### Description (GitHub About, 160 chars)
```
QAOA hub selection on 12-node global airport network. QUBO+Ising formulation, Qiskit Aer simulator, benchmarked vs brute-force & greedy at p=1,2,3.
```

### Topics
```
quantum-computing  qaoa  qiskit  qubo  ising-hamiltonian
combinatorial-optimization  airport-optimization  hub-selection
nisq  variational-quantum-algorithms  python  operations-research
quantum-approximate-optimization  aer-simulator  network-optimization
```

### Git Commands

```bash
cd path\to\qaoa-airport-optimisation

git init
git branch -M main
git add .
git commit -m "Initial commit: QAOA Airport Hub Optimisation

- 12-node global airport network (ATL, DXB, LHR, ORD, HND, LAX, CDG, DFW, FRA, IST, SIN, AMS)
- QUBO formulation with k=4 cardinality constraint (lambda=2.5)
- QUBO -> Ising mapping via x_i = (1 - sigma_z)/2 substitution
- Qiskit QAOA circuit: ZZ+Rz cost layer, Rx mixer, p=1,2,3 layers
- Hybrid COBYLA optimization loop with shot-based expectation value
- Benchmarked against brute-force (C(12,4)=495) and greedy heuristic
- Key finding: QAOA p>=2 discovers higher-efficiency solutions than QUBO minimum
- 7-panel dark-theme benchmark dashboard"

git remote add origin https://github.com/YOUR_USERNAME/qaoa-airport-optimisation.git
git push -u origin main
```

---

## After Pushing Both — GitHub Profile Steps

### 1. Add topics (both repos)
Repo page → gear icon ⚙️ next to "About" → paste topics → Save

### 2. Pin both repos
Your profile → "Customize your pins" → tick both → Save

### 3. Update cross-links
In both READMEs, replace `YOUR_USERNAME` with your actual GitHub username. Then:
```bash
git add README.md
git commit -m "Update cross-repo links with actual GitHub username"
git push
```

### 4. Add social preview images
Repo Settings → "Social preview" → upload `assets/qaoa_airport_results.png` (airport repo) and `assets/full_analysis.png` (silver futures repo). These appear when your link is shared on LinkedIn/Twitter.

---

## CV/Resume Bullet Points

### Option A — Both projects together (1 line each)

> **QAOA Noise Mitigation** | Python, PennyLane · [github.com/YOUR_USERNAME/qaoa-phase-space-finance](https://github.com)  
> Applied Wigner-function phase-space calibration to recover QAOA energy landscapes on NISQ hardware; Zero-Noise Extrapolation with Richardson polynomial extrapolation; silver futures Max-Cut routing problem.

> **QAOA Combinatorial Optimization** | Python, Qiskit · [github.com/YOUR_USERNAME/qaoa-airport-optimisation](https://github.com)  
> Complete QUBO/Ising QAOA pipeline for 12-node airport hub selection; benchmarked p=1,2,3 circuits against brute-force; discovered QAOA efficiency gain beyond QUBO minimum at p≥2.

### Option B — Combined entry (stronger if space allows)

> **Quantum Optimization Research Portfolio** | Python, PennyLane, Qiskit, NumPy, SciPy, NetworkX  
> Two self-directed projects applying QAOA to real-world combinatorial problems. (1) Silver futures execution routing: Wigner-function noise profiling + ZNE error mitigation bridging CV quantum optics with NISQ hardware decoherence. (2) Global airport hub selection: full QUBO→Ising pipeline on 12 qubits via Qiskit Aer; QAOA p=1,2,3 benchmarked against exact brute-force, discovering efficiency gains beyond the QUBO objective minimum.

---

## LinkedIn Project Descriptions

### Project 1 — Phase-Space Noise Calibration

**Title**: Phase-Space Noise Calibration for QAOA-Based Financial Optimization  
**Associated with**: Universität Paderborn  

> Developed a simulation bridging continuous-variable quantum optics with near-term quantum computing. Applied the law-of-total-variance calibration framework from my Master's thesis (balanced homodyne detection) to QAOA energy landscape recovery on NISQ hardware.
>
> Modelled silver futures execution routing as a weighted Max-Cut problem over 6 global trading venues. Wigner-function phase-space profiling derives ZNE noise scale factors; Richardson polynomial extrapolation recovers noiseless landscapes from noisy NISQ circuit outputs.
>
> **Stack**: PennyLane · NumPy/SciPy · NetworkX · Matplotlib · COBYLA

### Project 2 — QAOA Airport Hub Optimisation

**Title**: QAOA Airport Hub Optimisation — Hybrid Quantum-Classical Combinatorial Optimization  
**Associated with**: Self-Proposed Research Project  

> Implemented a complete QAOA pipeline to solve a hub selection problem on a 12-node global airport network. The problem is formulated as a QUBO with a cardinality constraint, mapped to an Ising Hamiltonian, and executed on IBM's Qiskit Aer quantum simulator at circuit depths p=1,2,3.
>
> Key finding: QAOA at p≥2 surfaces hub configurations with 67% higher efficiency scores than brute-force QUBO minimisation — demonstrating quantum variational search's ability to escape proxy-objective local optima.
>
> **Stack**: Qiskit · Qiskit Aer · NumPy/SciPy · NetworkX · Matplotlib · COBYLA

---

## What a Recruiter Sees When They Click Both Links

| What They Notice | Signal It Sends |
|---|---|
| Two different quantum frameworks (Qiskit + PennyLane) | You chose the right tool per problem, not just one you know |
| Two different domains (finance + aviation) | Cross-domain thinking; not a one-trick project |
| Dark-theme publication-quality figures | You care about presentation and communication |
| Honest Limitations sections | Research maturity; you understand your own work's scope |
| Cross-linked repos | You think about your work as a coherent portfolio |
| QUBO → Ising derivation documented | Mathematical depth beyond just calling library functions |
| ZNE + Wigner function bridging optics → QC | Genuinely novel conceptual contribution |
| Brute-force benchmarks included | You understand baselines and rigor |

---

## Short Portfolio Summary (for personal website or application portal)

> I have built two quantum computing simulation projects applying QAOA to real-world optimization problems. The first uses Wigner-function noise profiling — borrowed from my Master's thesis on balanced homodyne detection — to derive Zero-Noise Extrapolation calibration factors for NISQ hardware, applied to silver futures execution routing as a Max-Cut problem. The second implements a complete QUBO/Ising QAOA pipeline for global airport hub selection using IBM's Qiskit Aer simulator, benchmarked against classical exact and heuristic solvers. Both projects are fully documented and publicly available on GitHub.
