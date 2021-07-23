# VRPD_TSP_MA

## Structure of the Project
#### Direction #./Classes#: the classes like resources, nodes and managers
- resources: [Packages, Batteries, Weather], 
- nodes: [Minivan, Drones, Docking_hubs, Depot, Customers], 
- managers: [Route(manage the Depot, Docking_hubs and Customer nodes), 
             Vehicles(manage the Drones and Minivan), 
             PARAMs(manage all resources like Packages and Batteries)]
#### Direction #./Classes./methods#: the classes of using object with constrains
- father object of these Constrains classes: Constrains.py
- the object to manage activations of vans: Van_Constrains.py
- the object to manage activations of drones: Drone_Constrains.py
- the object to manage activations of depot and docking hubs: Station_Constrains.py

## the example to initiate
 currently, the code contains only initiation for the variables and needed parameters for the constrinas
 
 1. solution matrix: [van, drones] in GRB_Models.py in a form of pd.DataFrame
 2. constrains matrix: 
 - ['non_fly_zone', through function 'non_fly_zone_constrs()' to generate a dictionary that contains which customers live in a 'non fly zone'
 - 'customer_demand', through function 'demand_constrs()' to generate a dictionary that contains how many packages each customer require
 - 'weather_rate_matrix', through function 'weather_matrix_fn()' to generate a matrix in a form of DataFrame that presents how much the wind speed affects the weight of each eadege.
 - 'intersection_van_doc_num', through function 'get_package_backup(solution_matrix_van: DataFrame, solution_matrix_drones: list[DataFrame])' to count out how many docking hub nodes are covered by van, at where the van can reload packages 
 - 'intersection_dro_vanDoc_num', through function function 'get_package_backup(solution_matrix_van: DataFrame, solution_matrix_drones: list[DataFrame])' to count out how many van and docking hub nodes are covered by drones, at where the drones can reload packages
 - 'battery_intersections', through function 'get_battery_backup(solution_matrix_van: DataFrame, solution_matrix_drones: list[DataFrame])' to count out how many intersection nodes between drones and [docking hub and van], at where the drones can change batteries]
 
from Classes.methods.GRB_Var_Constrs import GRB_Var_Constrs

Var_Constrs = GRB_Var_Constrs()




## API of the project:
http://htmlpreview.github.io/?https://github.com/a411633308/VRPD_TSP_MA/blob/master/VRPD_TSP/build/html/index.html
