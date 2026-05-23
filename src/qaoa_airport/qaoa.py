import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter, ParameterVector
from qiskit_aer import AerSimulator
from .qubo import build_qubo, qubo_to_ising

backend = AerSimulator()

Q_MAT = build_qubo()
J_MAT, H_VEC, OFFSET = qubo_to_ising(Q_MAT)

def build_qaoa_circuit(J, h, p):
    n = J.shape[0]
    gamma = ParameterVector("γ", p)
    beta = ParameterVector("β", p)
    qc = QuantumCircuit(n)
    qc.h(range(n))  # initial |+> state

    for layer in range(p):
        # Problem unitary
        for i in range(n):
            for j in range(i+1, n):
                if abs(J[i,j]) > 1e-10:
                    qc.cx(i, j)
                    qc.rz(2 * gamma[layer] * J[i,j], j)
                    qc.cx(i, j)
        for i in range(n):
            if abs(h[i]) > 1e-10:
                qc.rz(2 * gamma[layer] * h[i], i)
        # Mixer
        for i in range(n):
            qc.rx(2 * beta[layer], i)
    qc.measure_all()
    return qc, gamma, beta


def qubo_cost(bitstring):
    x = np.array([int(b) for b in bitstring])
    return float(x @ Q_MAT @ x)
