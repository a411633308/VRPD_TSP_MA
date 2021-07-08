#!/usr/bin/python
# -*- coding: UTF-8 -*-

import networkx as nx
from Classes.Depot import Depot
from Classes.Docking_hubs import Docking_hubs
from Classes.Customers import Customers

import numpy as np
from random import choice
import random
# import matplotlib.pyplot as plt

class Routes:
    def __init__(self, bat_dock_num: int, drone_fly_range: int, cust_needs: dict):
        """
        the graph consist of docking hubs, depot and customers nodes
        :param bat_dock_num: int, the batteries number saved in docking hubs
        :param drone_fly_range: int, the maximum flying range of drone
        :param cust_needs: parameter for initiating class Customers
        """
        self.nodes_docking_hubs: list[Docking_hubs] = list()  # lists for nodes of docking hubs
        self.nodes_depot: list[Depot] = list()  # list for depots nodes
        self.nodes_graph: list = list()  # list for graph nodes
        self.nodes_customers: list[Customers] = list()  # list for customer nodes

        # params for initiating the related classes
        self.params_cust: dict = cust_needs
        self.bat_num_dock: int = bat_dock_num
        self.flying_range: int = drone_fly_range
        self.color_map: list[str] = list()
        self.G = nx.Graph()

    def init_graph_nodes(self, dckh_num: int, dep_num: int, cus_num: int):
        """
        init sequence of nodes for a graph
        :param dckh_num: int,
            the number of docking hub nodes in the graph
        :param dep_num: int,
            the number of depot nodes
        :param cus_num: int,
            the number of customer nodes
        :return: initiated graph
        """
        self.nodes_docking_hubs = [Docking_hubs(self.bat_num_dock, self.flying_range)
                                   for i in range(dckh_num)]
        self.nodes_depot = [Depot() for i in range(dep_num)]
        self.nodes_customers = [Customers(self.params_cust[0], self.params_cust[1])
                                for i in range(cus_num)]

        # list that contains the customers and docking hubs' nodes
        a: list = list()
        [a.append(self.nodes_docking_hubs[i]) for i in range(len(self.nodes_docking_hubs))]
        [a.append(self.nodes_customers[i]) for i in range(len(self.nodes_customers))]

        # random shuffles the order of elements in the list
        # the result from shuffle() will not be saved
        b = np.random.permutation(a)
        self.nodes_graph.append(choice(self.nodes_depot))
        [self.nodes_graph.append(b[i]) for i in range(len(b))]
        # customers and docking hubs nodes shuffled as a new element

        z = [str(self.nodes_graph[i].index) for i in range(len(self.nodes_graph))]
        [self.G.add_node(i, type=i[:3]) for i in z]
        [self.G.add_edge(i, j) for i in z for j in list(set(z)-{i})]
        return self.G

    def set_non_flying(self, non_fly_num: int):
        """
        set a number of customers live in "non flying range"
        :param self:
        :param non_fly_num: the number of the relevant customers
        :return: the related indexes of customer nodes
        """
        customers_indexes: list = list()
        [customers_indexes.append(choice(range(len(self.nodes_customers)))) for i in range(non_fly_num)]
        [self.nodes_customers[i].live_in_non_flying(True) for i in customers_indexes]
        return customers_indexes

    def set_color_weights_type(self, colors, weights):
        for n, nbrs in self.G.adj.items():
            i: int = 0
            if n[:3] == 'cus':
                self.color_map.append(colors[0])
            elif n[:3] == 'dep':
                self.color_map.append(colors[1])
            else:
                self.color_map.append(colors[2])

            for nbr, eattr in nbrs.items():
                eattr['weight_dro'] = round(weights[0][i], 3)
                eattr['weight_van'] = round(weights[1][i], 3)
                if eattr['weight_dro'] < eattr['weight_van']:
                    eattr['veh_type'] = 'drone'
                else:
                    eattr['veh_type'] = 'van'
                i = i+1
        return self.color_map
    # It's still short of graph with specific font size and format

#
# bat_num: int = 20
# fly_range: int = 236
# cus_needs: list = [1, False]
#
# route = Routes(bat_dock_num=bat_num, drone_fly_range=fly_range, cust_needs=cus_needs)
# graph = route.init_graph(dckh_num=6, dep_num=3, cus_num=36)
#
# route.set_non_flying(18)
#
# # initiate new graph with specific weights
# nodes_len: int = len(route.nodes_graph)
# drones_weights: list = list()
# random.seed(100)
# [drones_weights.append(random.random()*random.uniform(0, 15)) for i in range(nodes_len)]
# van_weights: list = list()
# [van_weights.append(random.random()*random.uniform(0, 15)) for i in range(nodes_len)]
#
# # plotting the graph
# color_map = route.set_color_weights_type(['skyblue', 'red', 'orange'],[drones_weights, van_weights])
# nx.draw(graph, node_color=color_map, with_labels=False)
# plt.show()
