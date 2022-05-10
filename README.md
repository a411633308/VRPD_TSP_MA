# VRPD_TSP_MA:

## Meta-Heuristic Algorithm Implementation
nodes, vehicles, and resources classes are in location of VRPD-TSP/Classes
related constraints formulation and SA algorithms are stored in VRPD-TSP/Classes/methods
the way to test as shown in VRPD-TSP/Classes/demo_Test.py

## Gurobi Mathematical Model 
- several functions used to search nodes' role and index as in "Functors.py"
- initiation of decision variables, cosntraints, and cost function and their optimization with Gurobi in "dictionary_pairs.py"
