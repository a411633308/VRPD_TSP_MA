#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.Routes import Routes
import random

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt


class Solution:
    def __init__(self, route_params: list = {3, 60, [1, False]}, non_fly_num: int = 3,
                 graph_params: list = {3,4,16},
                 seed_num: int = 1078, color_list: list = {'skyblue', 'red', 'orange'}):
        """
        Solution for graph and nodes
        :param route_params: batteries, flying range and customer needs
        :param non_fly_num: whether these customers live in a "non flying range"
        :param graph_params: numbers of docking hubs, depot, and customer nodes
        :param seed_num: used to generate drones and vans' weights randomly
        :param color_list: the color of customer, depot, and docking hub nodes
        """
        self.route_params_list: list = route_params
        self.graph_params_list: list = graph_params
        self.non_flying_num: int = non_fly_num
        self.adj_matrix: any = None
        self.dro_weight_matrix: any = None
        self.van_weight_matrix: any = None
        self.solution_matrix_drones: list = list()
        self.solution_matrix_van: bytearray = None

        # ------------initiate route and graph automatically------------
        self.route: Routes = Routes(bat_dock_num=self.route_params_list[0], drone_fly_range=self.route_params_list[1],
                                    cust_needs=self.route_params_list[2])
        self.graph = self.route.init_graph_nodes(dckh_num=self.graph_params_list[0], dep_num=self.graph_params_list[1],
                                                 cus_num=self.graph_params_list[2])
        # set several customers live in a "non flying range."
        self.route.set_non_flying(self.non_flying_num)
        # length of nodes exists in the graph
        self.nodes_len: int = len(self.route.nodes_graph)
        # ------------initiate route and graph automatically------------

        # ------------generate weights of drones and vans randomly------------
        self.weights: list = list()
        [self.weights.append(list()) for i in [0, 1]]

        # generate weights randomly with certain seed
        random.seed(seed_num)
        [self.weights[0].append(round(random.random() * random.uniform(0, 100), 3))
         for i in range(self.nodes_len * (self.nodes_len - 1))]  # generate drone weights
        [self.weights[1].append(round(random.random() * random.uniform(0, 100), 3))
         for i in range(self.nodes_len * (self.nodes_len - 1))]  # generate van weights

        # save to the relevant matrix
        self.dro_weight_matrix = self.weights[0]
        self.van_weight_matrix = self.weights[1]
        # ------------generate weights of drones and vans randomly------------

        self.color_map = self.route.set_color_weights_type(color_list, self.weights)

    def plot_graph(self):
        # print("edges and nodes numbers: ",self.graph.number_of_edges(),
        #       self.graph.number_of_nodes())
        pos = nx.spring_layout(self.route.G)
        nx.draw(self.graph, node_color=self.color_map, with_labels=False)

        # node_labels = nx.get_node_attributes(self.route.G, 'type')
        # nx.draw_networkx_labels(self.route.G, pos, labels=node_labels)

        edge_labels = nx.get_edge_attributes(self.route.G, 'weight_dro')
        nx.draw_networkx_edge_labels(self.route.G, pos, edge_labels=edge_labels)
        # edge_labels_2 = nx.get_edge_attributes(self.route.G, 'weight_van')
        # nx.draw_networkx_edge_labels(self.route.G, pos, edge_labels=edge_labels_2)
        plt.show()

    # generate solution matrix
    def weights_adj_matrix(self):
        """
        generate weights and adjacency matrix of the graph
        :return: 1
        """
        from pandas import DataFrame
        self.adj_matrix = DataFrame(nx.adjacency_matrix(self.graph, nodelist=self.graph.nodes()).todense(),
                                    columns=self.graph.nodes(), index=self.graph.nodes())

        # ------------transform the 1-d weights into 2-d matrix with 0 diagonal------------

        # ------weights matrix of drone------
        self.dro_weight_matrix = np.array(self.dro_weight_matrix)
        self.dro_weight_matrix = self.dro_weight_matrix.reshape((9, 8))
        a = self.dro_weight_matrix
        b = list(range(self.nodes_len))
        for i in range(len(a)):
            b[i] = a[i].tolist()
            b[i].insert(i, 0)
        self.dro_weight_matrix = DataFrame(np.array(b),
                                           columns=self.graph.nodes(), index=self.graph.nodes())
        # ------weights matrix of drone------

        # ------weights matrix of van------
        self.van_weight_matrix = np.array(self.van_weight_matrix)
        self.van_weight_matrix = self.van_weight_matrix.reshape((9, 8))
        a = self.van_weight_matrix
        b = list(range(self.nodes_len))
        for i in range(len(a)):
            b[i] = a[i].tolist()
            b[i].insert(i, 0)
        self.van_weight_matrix = DataFrame(np.array(b),
                                           columns=self.graph.nodes(), index=self.graph.nodes())
        # ------weights matrix of van------
        # ------------transform the 1-d weights into 2-d matrix with 0 diagonal------------

        return 1

    def generate_solution_matrix_randomly(self, drones_num: int):
        """
        generate the solution matrix of the drones and van
        :return:
        """
        self.solution_matrix_van = np.random.randint(0, 2, (9, 9))
        [self.solution_matrix_drones.append(np.random.randint(0, 2, (9, 9))) for i in range(drones_num)]
        print("randomly generated solution matrix for van\n", self.solution_matrix_van)
        print("randomly generated solution matrix for drones\n", self.solution_matrix_drones)

# route_params: list = [2, 200, [random.choice(range(0, 1)), False]]
# non_fly_num: int = 1
# graph_params: list = [2, 3, 6]
# # the color of customer, depot and docking hub nodes: skyblue, red, and orange
# initial_solution = Solution(route_params=route_params, graph_params=graph_params, seed_num=1200,
#                             non_fly_num=non_fly_num, color_list=['skyblue', 'red', 'orange'])
# # initial_solution.plot_graph()  # plot the complete graph
# # ---initiate the related parameters to generate solution matrices
# initial_solution.weights_adj_matrix()
# # ------generate matrix randomly
# initial_solution.generate_solution_matrix_randomly(2)
# # ------whether the solution satisfy the requirements

