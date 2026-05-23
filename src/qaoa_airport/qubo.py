import numpy as np
from .data import AIRPORTS, ROUTES, K_HUBS, LAMBDA

def build_qubo():
    N = len(AIRPORTS)
    Q = np.zeros((N, N))
    pax_max = max(a["pax_M"] for a in AIRPORTS.values())
    for i in range(N):
        d_i = -(1.0 - AIRPORTS[i]["otd"])*0.8
        p_i = AIRPORTS[i]["pax_M"]/pax_max * 0.5
        Q[i,i] = d_i - p_i + LAMBDA*(1 - 2*K_HUBS)
    for (i,j),w in ROUTES.items():
        if i < j:
            Q[i,j] += -w + 2*LAMBDA
            Q[j,i] = Q[i,j]
    return Q

def qubo_to_ising(Q):
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
