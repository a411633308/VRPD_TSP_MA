#!/usr/bin/python
# -*- coding: UTF-8 -*-

import networkx as nx
from Classes.Depot import Depot
from Classes.Docking_hubs import Docking_hubs
from Classes.Customers import Customers

import numpy as np
import random
from random import choice
from Classes.PARAMs import seed_num, max_bat_num_dockhub, max_pack_num_dockhub, \
    flying_range_drone, customer_needs, dockhub_num, depot_num, customer_num, color_list
# import matplotlib.pyplot as plt

class Routes:
    def __init__(self, bat_dock_num: int = max_bat_num_dockhub, drone_fly_range: int = flying_range_drone,
                 cust_needs: dict = customer_needs):
        """
        the graph consist of docking hubs, depot and customers nodes
        :param bat_dock_num: int, the batteries number saved in docking hubs
        :param drone_fly_range: int, the maximum flying range of drone
        :param cust_needs: parameter for initiating class Customers
        """
        random.seed(seed_num)
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

        self.fix_position: dict = dict()

        self.init_graph_nodes()
        self.set_non_flying()
        self.set_color_weights_type(color_list)

        self.plot_map(r'G:\Unterricht\05-2021\Ipad_Sharing\MA\Routing\8th_Random_Graphs\map_graph.png')

    def init_graph_nodes(self, dckh_num: int = dockhub_num, dep_num: int = depot_num, cus_num: int = customer_num):
        """
        init sequence of nodes for a graph
        :param dckh_num: int, the number of docking hub nodes in the graph
        :param dep_num: int, the number of depot nodes
        :param cus_num: int, the number of customer nodes
        :return: initiated graph
        """
        self.nodes_docking_hubs = [Docking_hubs(self.bat_num_dock, self.flying_range)
                                   for i in range(dckh_num)]
        self.nodes_depot = [Depot() for i in range(dep_num)]
        import random
        long: list = random.sample(range(0, cus_num*cus_num), cus_num*2)
        self.nodes_customers = [Customers(self.params_cust[0], self.params_cust[1],
                                          longtitude= long[i], latitude= long[-i])
                                for i in range(cus_num)]

        # list that contains the customers and docking hubs' nodes
        a: list = list()
        [a.append(self.nodes_docking_hubs[i]) for i in range(len(self.nodes_docking_hubs))]
        [a.append(self.nodes_customers[i]) for i in range(len(self.nodes_customers))]

        # random shuffles the order of elements in the list
        # the result from shuffle() will not be saved
        b = np.random.permutation(a)
        self.G = nx.Graph()

        self.nodes_graph = list()
        self.nodes_graph.append(self.nodes_depot[0])
        [self.nodes_graph.append(b[i]) for i in range(len(b))]
        self.nodes_graph.append(self.nodes_depot[-1])

        # customers and docking hubs nodes shuffled as a new element
        z = [self.nodes_graph[i].index for i in range(len(self.nodes_graph))]
        # self.G.add_node(self.nodes_depot[0])
        # [print(i.type) for i in self.nodes_graph[1:]]
        # self.G.add_nodes_from(self.nodes_graph[1:])
        [self.G.add_node(z[i], type=self.nodes_graph[i].type, long=self.nodes_graph[i].long,
                         lat=self.nodes_graph[i].lat) for i in range(len(z))]

        self.fix_position: dict = dict()
        [self.fix_position.update({self.nodes_graph[i].index:
                                       [self.nodes_graph[i].long,
                                        self.nodes_graph[i].lat]})
         for i in range(len(z))]

        for i in range(len(z)*3):
            a = random.choice(z)
            b = random.choice(z)
            if a != b:
                self.G.add_edge(a, b)

        return self.G

    def plot_map(self, graph_url: str):
        import matplotlib.pyplot as plt
        plt.rcParams['figure.figsize'] = (40, 40)
        plt.rcParams['font.size'] = 50
        plt.title('Connection Map Graph')
        pos = nx.spring_layout(self.G,  seed=seed_num)
        nx.draw(self.G, node_color=self.color_map, with_labels=True, node_size=1200, font_size=25)
        plt.savefig(graph_url)
        plt.close()

    def set_non_flying(self):
        """
        set a number of customers live in "non flying range"
        :param self:
        :param non_fly_num: the number of the relevant customers
        :return: the related indexes of customer nodes
        """
        from Classes.PARAMs import non_fly_num
        customers_indexes: list = list()
        [customers_indexes.append(choice(range(len(self.nodes_customers)))) for i in range(non_fly_num)]
        [self.nodes_customers[i].live_in_non_flying() for i in customers_indexes]
        return customers_indexes

    def set_color_weights_type(self, colors):
        for n, nbrs in self.G.adj.items():
            if n[:3] == 'cus':
                self.G.nodes[n]['type'] = 'customer'
                self.color_map.append(colors[0])
                cus_node: Customers = self.find_node(n)
                if type(cus_node) == type(self.nodes_customers[0]):
                    self.G.nodes[n]['non_fly_zone'] = cus_node.in_non_flying
                    self.G.nodes[n]['demand'] = cus_node.pack_needs # default as 1, but actually need to recall with searching function
            elif n[:3] == 'dep':
                self.G.nodes[n]['type'] = 'depot'
                self.G.nodes[n]['demand'] = 0
                self.G.nodes[n]['non_fly_zone'] = 0
                self.color_map.append(colors[1])
                for nbr, eattr in nbrs.items():
                    eattr['van_dro_set'] = 1
            elif n[:3] == "doc":
                self.G.nodes[n]['demand'] = 0
                self.G.nodes[n]['non_fly_zone'] = 0
                self.G.nodes[n]['type'] = 'docking hub'
                self.color_map.append(colors[2])
                self.G.nodes[n]['max_ba'] = max_bat_num_dockhub
                self.G.nodes[n]['max_pa'] = max_pack_num_dockhub

            for nbr, eattr in nbrs.items():
                # if self.G.nodes[n]['non_fly_zone'] == 1:
                #     eattr['non_fly_zone'] = 1
                # else:
                #     eattr['non_fly_zone'] = 0

                # -------- set the customer demand according to the node attribution
                if self.G.nodes[n]['demand'] == 1:
                    eattr['demand'] = 1
                else:
                    eattr['demand'] = 0
                # -------- set the euclidean distance between nodes as the weight of their connection
                eattr['weight'] = 0
                # get the related Object class according to index from the NetworkX
                node_1 = self.find_node(n)
                node_2 = self.find_node(nbr)
                if type(node_1)!=type(ValueError):
                    import numpy as np
                    vec1 = np.array([node_1.lat, node_1.long])
                    vec2 = np.array([node_2.lat, node_2.long])
                    #distance_1 = round(np.linalg.norm(vec1-vec2))
                    distance_1 = np.sqrt(np.sum(np.square(vec1-vec2)))/13
                    eattr['weight'] = round(distance_1, 2)
                # -------- set the wind direction according to the node attribution
                eattr['wind_direction'] = node_1.wind_direction*node_2.wind_direction

                # -------- set the costs of the drones to avoid risks area
                eattr['detour_risks'] = np.random.uniform(0,5)
        return self.color_map
    # It's still short of graph with specific font size and format

    def find_node(self, cus_index: str):
        found_index = [i for i in range(len(self.nodes_graph))
                       if self.nodes_graph[i].index==cus_index]
        if len(found_index)>0:
            return self.nodes_graph[found_index[0]]
        else:
            return ValueError

