#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.Routes import Routes
import random

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from Classes.PARAMs import color_list, seed_num, graph_params_list, route_params_list, non_fly_num
from Classes.PARAMs import customer_num, dockhub_num, drones_num_on_van


class Solution:
    def __init__(self, route_params: list = route_params_list, non_fly_num: int = non_fly_num,
                 graph_params: list = graph_params_list,
                 seed_num: int = seed_num, color_list: list = color_list):
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

        # ------------initiate route and graph automatically--------------------------------
        self.route: Routes = Routes(bat_dock_num=self.route_params_list[0], drone_fly_range=self.route_params_list[1],
                                    cust_needs=self.route_params_list[2])
        self.graph = self.route.init_graph_nodes(dckh_num=self.graph_params_list[0], dep_num=self.graph_params_list[1],
                                                 cus_num=self.graph_params_list[2])
        # set several customers live in a "non flying range."
        self.route.set_non_flying(self.non_flying_num)
        # length of nodes exists in the graph
        self.nodes_len: int = len(self.route.nodes_graph)
        # ------------initiate route and graph automatically-------------------------------

        # ------------generate weights of drones and vans randomly-------------------------
        # self.weights: list = list()
        # # [self.weights.append(list()) for i in [0, 1]]
        #
        # # generate weights randomly with certain seed
        # random.seed(seed_num)
        # [self.weights.append(round(random.random() * random.uniform(0, 100), 3))
        #  for i in range(len(self.graph.edges()))]  # generate drone weights
        # [self.weights.append(round(random.random() * random.uniform(0, 100), 3))
        #  for i in range(len(self.graph.edges()))]  # generate van weights
        # save to the relevant matrix
        self.dro_weight_matrix: any
        self.van_weight_matrix: any
        # ------------generate weights of drones and vans randomly------------------------

        self.color_map = self.route.set_color_weights_type(color_list)
        self.graph = self.route.G

        # ------------ variables for the Gurobi ------------------------------------------
        self.customer_demand: dict = dict()
        self.non_fly_zone: dict = dict()
        self.dro_connection_matrix: any
        self.van_connection_matrix: any
        self.nodes_oder = [self.route.nodes_graph[i].index for i in range(len(self.route.nodes_graph))]

    def plot_graph_droWeight(self, graph_url: str):
        """
        plot the graph with drone weight as label of the edge
        :param graph_url: the url address to save the iamge
        :return: none
        """
        # print("edges and nodes numbers: ",self.graph.number_of_edges(),
        #       self.graph.number_of_nodes())
        plt.rcParams['figure.figsize'] = (40, 40)
        plt.rcParams['font.size'] = 50
        plt.title('Map Graph with Weights of Drone')

        nx.draw(self.graph, node_color=self.color_map, with_labels=True, node_size=1200, font_size=25)
        pos = nx.spring_layout(self.route.G)

        edge_labels = nx.get_edge_attributes(self.route.G, 'weight_dro')
        nx.draw_networkx_edge_labels(self.route.G, pos, edge_labels=edge_labels, font_size=25)
        # edge_labels_2 = nx.get_edge_attributes(self.route.G, 'weight_van')
        # nx.draw_networkx_edge_labels(self.route.G, pos, edge_labels=edge_labels_2)

        plt.savefig(graph_url)
        plt.close()

    def plot_graph_vanWeight(self, graph_url: str):
        """
        plot the graph with van weight as label of the edge
        :param graph_url: the url address to save the iamge
        :return: none
        """
        # print("edges and nodes numbers: ",self.graph.number_of_edges(),
        #       self.graph.number_of_nodes())
        plt.rcParams['figure.figsize'] = (40, 40)
        plt.rcParams['font.size'] = 50
        plt.title('Map Graph with Weights of Van')

        nx.draw(self.graph, node_color=self.color_map, with_labels=True, node_size=1200, font_size=25)
        pos = nx.spring_layout(self.route.G)

        edge_labels = nx.get_edge_attributes(self.route.G, 'weight_van')
        nx.draw_networkx_edge_labels(self.route.G, pos, edge_labels=edge_labels, font_size=25)
        # edge_labels_2 = nx.get_edge_attributes(self.route.G, 'weight_van')
        # nx.draw_networkx_edge_labels(self.route.G, pos, edge_labels=edge_labels_2)

        plt.savefig(graph_url)
        plt.close()

    def non_fly_zone_constrs(self):
        """
        return whether the customers live in a "non fly zone" in a sequence of nodes in the weight matrix of the drones and van
        :return: the dictionary of the "non fly zone" constrains
        """
        temp = nx.get_node_attributes(self.route.G, name='non_fly_zone')
        self.weights_adj_matrix()
        a_temp = self.dro_weight_matrix[1]
        [self.non_fly_zone.update({j: True}) if temp[j] else self.non_fly_zone.update({i: False}) for i in a_temp for j in temp]
        return self.non_fly_zone

    def demand_constrs(self):
        """
        return customer demand in a sequence of nodes in the weight matrix of the drones and van
        :return: the dictionary of the customer demand
        """
        # temp = nx.get_node_attributes(self.route.G, name='demand')
        # self.weights_adj_matrix()
        # a_temp = self.dro_weight_matrix[1]
        # [self.customer_demand.update({i: temp[j]}) if i == j else self.customer_demand.update({i: 0})
        #  for i in a_temp for j in temp]
        # return self.customer_demand

    def dro_connection_constrs(self):
        nx.attr_matrix(self.route.G, edge_attr='weight_van')
        self.dro_connection_matrix = nx.attr_matrix(self.graph, edge_attr='veh_dro')
        print(self.dro_connection_matrix)

    def weight_matrix_fn(self):
        self.dro_weight_matrix = nx.attr_matrix(self.route.G, edge_attr='weight_dro', rc_order=self.nodes_oder)
        self.van_weight_matrix = nx.attr_matrix(self.route.G, edge_attr='weight_van', rc_order=self.nodes_oder)
        print(self.van_weight_matrix, '\n', len(self.van_weight_matrix))


# generate solution matrix
    def weights_adj_matrix(self):
        """
        generate weights and adjacency matrix of the graph
        :return: 1
        """
        # from pandas import DataFrame
        # self.adj_matrix = DataFrame(nx.adjacency_matrix(self.graph, nodelist=self.graph.nodes()).todense(),
        #                            columns=self.graph.nodes(), index=self.graph.nodes())

        # self.adj_matrix = nx.adjacency_matrix(self.graph).todense()
        self.adj_matrix = nx.adjacency_matrix(self.graph)

        self.van_weight_matrix = nx.attr_matrix(self.route.G, edge_attr='weight_van')
        self.dro_weight_matrix = nx.attr_matrix(self.route.G, edge_attr='weight_dro')
        # print("adjacency matrix: \n", self.adj_matrix)
        # print("type of the matrix: ", type(self.dro_weight_matrix))
        # print(self.dro_weight_matrix[0])
        # print("name of nodes: ", self.dro_weight_matrix[1])
        return 1

    def generate_solution_matrix_randomly(self):
        """
        generate the solution matrix of the drones and van
        :return: a list: [solution matrix for the van, solution matrixes for the drones on the van]
        """
        shape = len(self.graph.nodes())
        self.solution_matrix_van = np.random.randint(0, 2, (shape, shape))
        [self.solution_matrix_drones.append(np.random.randint(0, 2, (shape, shape))) for i in range(drones_num_on_van)]
        # print("randomly generated solution matrix for van\n", self.solution_matrix_van)
        # print("randomly generated solution matrix for drones\n", self.solution_matrix_drones)
        return self.solution_matrix_van, self.solution_matrix_drones


initial_solution = Solution()

# ---initiate the related parameters to generate solution matrices

# initial_solution.weights_adj_matrix()
# ------generate matrix randomly
solution_van, solution_drones = initial_solution.generate_solution_matrix_randomly()

# initial_solution.weights_adj_matrix()
initial_solution.non_fly_zone_constrs()
# initial_solution.route.plot_map(r'G:\Unterricht\05-2021\Ipad_Sharing\MA\Routing\8th\randomly_map_graph.png', initial_solution.color_map)
#
# initial_solution.plot_graph_droWeight(r'G:\Unterricht\05-2021\Ipad_Sharing\MA\Routing\8th\randomly_map_graph_dro.png')  # plot the complete graph
# initial_solution.plot_graph_vanWeight(r'G:\Unterricht\05-2021\Ipad_Sharing\MA\Routing\8th\randomly_map_graph_van.png')
# ------whether the solution satisfy the requirements
