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
from Classes.Station_Constrains import Depot_Constrains
depot_constrains = Depot_Constrains()

## API of the project:
http://htmlpreview.github.io/?https://github.com/a411633308/VRPD_TSP_MA/blob/master/VRPD_TSP/build/html/index.html
