# VRPD_TSP_MA:


## Description
Express delivery #vehicle combination with a van and several drones#, which is test with two in this thesis.
  - an OVRP, that does not require all vehicles to come back to depot again


In a network with three different nodes:
  - depot node: the van with drones will launch there with full charged batteries and loaded packages
  - docking hub node: drones can launch there through a special basestation, new full charged batteries and packges for the vehicle
  - customer node: the one who requires packages
  
constraints included in this project:
  - wind speed and its affect to the drone' distribution, in a way of increasing or decreasing cthe cost
  - relevant polocy of flying drone, whether a node is in a range of "no fly area"
  - the overall energy cost of the vehicles <= maximum energy they can access from depot and docking hub
  - the overall packages of the vehicles delivered <= maximum packages they can access from the depot and docking hub 
  - routes related to the depot node will no be covered by the drones
  
## Mathematical Formulation as in file "MathFormulation_20-30.pdf"

## Meta-Heuristic Algorithm Implementation
nodes, vehicles, and resources classes are in location of VRPD-TSP/Classes
related constraints formulation and SA algorithms are stored in VRPD-TSP/Classes/methods
the way to test as shown in VRPD-TSP/Classes/demo_Test.py

## Gurobi Mathematical Model 
- several functions used to search nodes' role and index as in "Functors.py"
- initiation of decision variables, cosntraints, and cost function and their optimization with Gurobi in "dictionary_pairs.py"
