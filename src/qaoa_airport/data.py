import networkx as nx
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
