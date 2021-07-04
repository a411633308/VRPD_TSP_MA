#!/usr/bin/python
# -*- coding: UTF-8 -*-

import networkx as nx
from Classes.Depot import Depot
from Classes.Docking_hubs import Docking_hubs
from Classes.Customers import Customers

import matplotlib as plt

import matplotlib.pyplot as plt

import numpy as np
import random
from random import choice


class Route:
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

    def init_graph(self, dckh_num: int, dep_num: int, cus_num: int):
        """
        init sequence of nodes for a graph
        :param dckh_num: int,
            the number of docking hub nodes in the graph
        :param dep_num: int,
            the number of depot nodes
        :param cus_num: int,
            the number of customer nodes
        :return: 1
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
        return 1

    def set_non_flying(self, non_fly_num: int):
        """
        set a number of customers live in "non flying range"
        :param self:
        :param non_fly_num: the number of the relevant customers
        :return: the related indexes of customer nodes
        """
        customers_indexes: list = list()
        [customers_indexes.append(choice(range(len(self.nodes_customers))))
         for i in range(non_fly_num)]
        [self.nodes_customers[i].live_in_non_flying(True) for i in customers_indexes]
        return customers_indexes

    def set_nodes_color_type(self, colors, G):
        for n, nbrs in G.adj.items():
            if n[:3] == 'cus':
                self.color_map.append(colors[0])
            else:
                self.color_map.append(colors[1])

            for nbr, eattr in nbrs.items():
                eattr['type'] = n[:3]
        return self.color_map


bat_num: int = 20
fly_range: int = 236
cus_needs: list = [1, False]
route = Route(bat_dock_num=bat_num, drone_fly_range=fly_range, cust_needs=cus_needs)
route.init_graph(dckh_num=6, dep_num=3, cus_num=36)
a = route.set_non_flying(18)

z = [str(route.nodes_graph[i].index) for i in range(len(route.nodes_graph))]
# z = route.nodes_graph
G = nx.Graph()
# [G.add_node(z[i], type=type(route.nodes_graph[i])) for i in range(len(z))]


G = nx.path_graph(z)
print(G.nodes())
[G.add_edge(choice(z), choice(z)) for i in range(len(z))]
[G.add_edge(choice(z), choice(z)) for i in range(26)]

color_map = route.set_nodes_color_type(['skyblue', 'orange'], G)
print("length of graphic nodes and color maps", len(G.nodes()), len(color_map))
nx.draw(G, node_color=color_map, with_labels=False)

plt.show()
