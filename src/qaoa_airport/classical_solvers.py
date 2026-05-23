import itertools
import time
import numpy as np
from .data import AIRPORTS, K_HUBS
from .qubo import Q_MAT

def brute_force():
    t0 = time.time()
    best_cost, best_subset = float("inf"), None
    for combo in itertools.combinations(range(len(AIRPORTS)), K_HUBS):
        x = np.zeros(len(AIRPORTS))
        x[list(combo)] = 1.0
        cost = float(x @ Q_MAT @ x)
        if cost < best_cost:
            best_cost, best_subset = cost, list(combo)
    return best_subset, best_cost, time.time() - t0


def greedy():
    t0 = time.time()
    selected, remaining = [], list(range(len(AIRPORTS)))
    for _ in range(K_HUBS):
        best_gain, best_node = float("inf"), None
        for node in remaining:
            candidate = selected + [node]
            x = np.zeros(len(AIRPORTS))
            x[candidate] = 1.0
            cost = float(x @ Q_MAT @ x)
            if cost < best_gain:
                best_gain, best_node = cost, node
        selected.append(best_node)
        remaining.remove(best_node)
    x = np.zeros(len(AIRPORTS))
    x[selected] = 1.0
    return selected, float(x @ Q_MAT @ x), time.time() - t0
