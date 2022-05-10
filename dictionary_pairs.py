import sys
import math
import random
import Functors

from itertools import combinations
import gurobipy as gp
from gurobipy import GRB

# set the cost rate of the vehicles
# set the number of drones
r_dro = random.uniform(0, 0.3)
r_van = random.uniform(0.3, 0.5)
_dro_num = 1

# 1. small scale network generation: depot, docking hub, and customer nodes number
####### when not enough parameters gave
if len(sys.argv) < 4:
    print('Usage: numbers of depot, docking hub, customer nodes. ')
    sys.exit(1)
####### save given parameters
_l = int(sys.argv[1])  # get the given first value from the parse argument for the number of depot nodes
_n = int(sys.argv[2])  # second argument, the number of docking hub nodes
_m = int(sys.argv[3])  # third argument, the number of customer nodes
####### generate nodes' location randomly
random.seed(3)
_points_dep = [(random.randint(0, 100), random.randint(0, 100)) for i in range(_l)]
_points_doc = [(random.randint(0, 100), random.randint(0, 100)) for i in range(_n)]
_points_cus = [(random.randint(0, 100), random.randint(0, 100)) for i in range(_m)]
####### the role dictioanry of corrensponding nodes
# create the corresponding dictionary for searching
role_list = {'depot': _points_dep, 'docking hubs': _points_doc, 'customer': _points_cus}
####### the index dictionary of corresponding nodes {0:(0, 1), 1:(0,2)}
points_temp = _points_dep + _points_doc + _points_cus  # Combine all points together into another dictionary
index_list = dict()
[index_list.update({i: points_temp[i]}) for i in range(len(points_temp))]

# 2. nodes' Euclidean Distance generation
####### the distance of two nodes, which are marked with their indexes
distance: dict = dict()
var = {distance.update({(i, j): math.sqrt(
    sum(
        (index_list[i][k] - index_list[j][k]) ** 2 for k in range(2))
)
})
    for i in index_list.keys() for j in index_list.keys() if i != j}


# 3. relevant parameters corresponding to constraints
####### no-fly areas
polocy_fac = Functors.nofly_generator(distance, points_temp)
####### drones will not cover routes that connects a depot node: important to define a vehicle combination
for i in polocy_fac:
    if Functors.nodes_role(role_list, index_list[i[0]]) == 'depot' or \
       Functors.nodes_role(role_list, index_list[i[1]]) == 'depot':
        polocy_fac[i] = 0   # form: {(0, 1): 0, (0, 2): 0}

####### energy restriction of each van and drone
energy_van = random.randint(400, 500)
energy_dro = random.randint(100, 200)
#######  packages restriction of each van and drone
package_van = random.randint(100,200)
package_dro = random.randint(3, 10)
####### weather factor to the cost of the drones
wind_dro = {i: random.uniform(-0.2, 0.2) for i in distance}
####### parameters of two vehicles for the cost function
van_cost = {('van', i[0], i[1]): distance[i] * r_van for i in distance}
dro_cost = {('dro', i[0], i[1]): distance[i] * r_dro * (1 + wind_dro[i]) for i in distance}
cost = dict(list(van_cost.items()) + list(dro_cost.items()))
####### list of routes that connect to a customer nodes
customer_routes = Functors.routes_role(_distance=distance, _role_list=role_list, _index_list=index_list, _role='customer')
depot_routes = Functors.routes_role(_distance=distance, _role_list=role_list, _index_list=index_list, _role='depot')
docking_routes = Functors.routes_role(_distance=distance, _role_list=role_list, _index_list=index_list, _role='docking hubs')



# # Callback - use lazy constraints to eliminate sub-tours
# def subtourelim(model, where):
#     if where == GRB.Callback.MIPSOL:
#         vals = model.cbGetSolution(model._vars)
#         # find the shortest cycle in the selected edge list
#         tour = subtour(vals)
#         # print("------------------- model._vars ", model._vars)
#         # print("------------------- quick sum of combinations ", gp.quicksum(model._vars[i, j] for i, j in combinations(tour, 2)))
#         if len(tour) < sum([_m,_n,_l]):
#             # add subtour elimination constr. for every pair of cities in tour
#             model.cbLazy(gp.quicksum(model._vars[i, j]
#                                      for i, j in combinations(tour, 2))
#                          <= len(tour)-1)
#
#
# # Given a tuplelist of edges, find the shortest subtour
# def subtour(vals):
#     # print('============= vals: ', vals)
#     # make a list of edges selected in the solution
#     edges = gp.tuplelist((i, j) for i, j in vals.keys()
#                          if vals[i, j] > 0.5)
#
#     # print('============= edges: ', edges)
#     unvisited = list(range(sum([_m,_n,_l])))
#     # print('============= unvisited: ', unvisited)
#     cycle = range(sum([_m,_n,_l])+1)  # initial length has 1 more city
#     while unvisited:  # true if list is non-empty
#         thiscycle = []
#         neighbors = unvisited
#         while neighbors:
#             current = neighbors[0]
#             thiscycle.append(current)
#             unvisited.remove(current)
#             neighbors = [j for i, j in edges.select(current, '*')
#                          if j in unvisited]
#         if len(cycle) > len(thiscycle):
#             cycle = thiscycle
#
#     # print('============= cycle: ', cycle)
#     return cycle
#
#


# 4. a new gurobi model
m = gp.Model()
vars = m.addVars(cost.keys(), obj=cost, vtype=GRB.BINARY, name='vehicles')
# variables key: ('dro', 1, 0)

####### polocy constraint
m.addConstrs(vars.sum('dro', i[0], i[1]) <= polocy_fac[i]*dro_cost[('dro', i[0], i[1])] for i in distance.keys())

####### customer requirements constraints
m.addConstrs(len(vars.select('*', i[0], i[1])) >= 1 for i in customer_routes)


####### energy constraint of van and drone
a = len(depot_routes)
b = len(docking_routes)
m.addConstrs(vars.sum('van', i[0], i[1]) <= a*energy_van for i in depot_routes)
m.addConstrs(vars.sum('dro', i[0], i[1]) <= a*energy_dro for i in depot_routes)
m.addConstrs(vars.sum('van', i[0], i[1]) <= b*energy_van for i in docking_routes)
m.addConstrs(vars.sum('dro', i[0], i[1]) <= b*energy_dro for i in docking_routes)
####### package constraint of van and drone
m.addConstrs(len(vars.select('van', i[0], i[0])) <= len(vars.select('van', j[0], j[1]))
             for i in customer_routes for j in docking_routes + depot_routes)
m.addConstrs(len(vars.select('dro', i[0], i[0])) <= len(vars.select('dro', j[0], j[1]))
             for i in customer_routes for j in docking_routes + depot_routes)
####### accomplite tasks through allowing repeatitive routes covered before
m.addConstrs(sum(vars.select('*', i, '*')) >= 2 for i in range(sum([_l,_n,_m])))
# for i, j in vars.keys():
#     vars[j, i] = vars[i, j]  # edge in opposite direction

#
# m.addConstrs(vars.sum(i, '*') == 2 for i in range(sum([_l,_n,_m])))
#
#
m._vars = vars
# m.Params.LazyConstraints = 1
m.optimize()
#
# vals = m.getAttr('X', vars)
# tour = subtour(vals)
# assert len(tour) == sum([_m,_n,_l])
#
# names: list = []
# [names.append((nodes_types(points_list[i]), points_list[i])) for i in tour]
#
print('')
# print('Optimal tour: %s' % str(tour))
# print('That is, the tour: ', names)
print('Optimal cost: %g' % m.ObjVal)
print('')