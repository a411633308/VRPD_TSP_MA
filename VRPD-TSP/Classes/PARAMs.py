#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

# ---------------------- params for the vehicles -------------------------------------------
drones_num_on_van: int = 2  # the number of drones on the minivan
van_num: int = 1  # the number of minivan used in a single TSP-D problem
flying_range_drone: float = 60
max_range_van: float = 500
rate_load_range_drone: float = random.uniform(0, 0.1)  # how many packages should be loaded according to the left energy
rate_load_range_van: float = random.uniform(0.3, 0.5)
rate_load_pack_drone: float = random.uniform(0.1, 0.2)  # how much !a package! affects its left battery state
rate_load_pack_van: float = random.uniform(0.3, 0.5)

# ---------------------- params for the packages -------------------------------------------
max_pack_num_dro: int = 3
max_pack_num_van: int = 20  # the maximum packages that store on the minivan
max_pack_num_dockhub: int = 50  # the maximum packages that can store at a docking hub
default_drone_pack_num: int = 3  # the number of packages for its maximum flying range

# ---------------------- params for the batteries -----------------------------------------
max_bat_num_van: int = 2  # the maximum batteries can be saved on a minivan
max_bat_num_dockhub: int = 5  # the maximum batteries can be saved at a docking hub

# ---------------------- params for the map -----------------------------------------------
dockhub_num: int = 3  # the number of docking hub nodes on the map to transport
depot_num: int = 2  # the number of depot on the map, only one is chosen
customer_num: int = 10  # the number of customers in the map
customer_needs: dict = [2, 0]  # [the number of packages the customer needs, whether lives in a "non flying range"]

# ---------------------- params for initiating a map graph --------------------------------
color_list: list = ['skyblue', 'red', 'orange']
seed_num: int = 178    # random seed to generate the location of docking hubs, depot and customer nodes
graph_params_list: list = [dockhub_num, depot_num, customer_num]    # params needed to generate a solution
route_params_list: list = [max_bat_num_dockhub, flying_range_drone, customer_needs]
non_fly_num: int = 1    # the number of customers who live in a non flying range

# ---------------------- params for simulated annealing algorithm -------------------------
obj_threshold: float = 200
initial_temp = 90
final_temp = 1
alpha = 3

fixed_cost: int = 300