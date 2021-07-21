#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.Routes import Routes
import random

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from Classes.PARAMs import color_list, seed_num, graph_params_list, route_params_list, non_fly_num
from Classes.PARAMs import customer_num, dockhub_num, drones_num_on_van, rate_load_pack_drone, rate_load_pack_van


class GRB_Var_Constrs:
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
        self.weight_matrix: any = None
        # self.van_weight_matrix: any = None
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
        self.dro_rate_load_matrix: any
        self.van_rate_load_matrix: any

        # ------------ the number of drone and van that have intersections ---------------
        self.intersection_numbers: list = list()

    def plot_graph_Weight(self, graph_url: str):
        """
        plot the graph with van weight as label of the edge
        :param graph_url: the url address to save the iamge
        :return: none
        """
        # print("edges and nodes numbers: ",self.graph.number_of_edges(),
        #       self.graph.number_of_nodes())
        plt.rcParams['figure.figsize'] = (50, 50)
        plt.rcParams['font.size'] = 55
        plt.title('Map Graph with Weights as Edge Labels')

        node_labels = nx.get_node_attributes(self.route.G, 'type')
        edge_labels = nx.get_edge_attributes(self.route.G, 'weight')
        pos = nx.spring_layout(self.route.G, seed=seed_num)

        nx.draw_networkx_edge_labels(self.route.G, pos, edge_labels=edge_labels, font_size=30)
        nx.draw_networkx_labels(self.route.G, pos, labels=node_labels, font_size=30)

        nx.draw(self.graph, node_color=self.color_map, pos=pos, with_labels=False, node_size=1500, font_size=30)
        plt.savefig(graph_url)
        plt.close()

    def non_fly_zone_constrs(self):
        """
        return whether the customers live in a "non fly zone" in a sequence of nodes in the weight matrix of the drones and van
        :return: the dictionary of the "non fly zone" constrains
        """
        temp = nx.get_node_attributes(self.route.G, name='non_fly_zone')

        for i in self.nodes_oder:
            self.non_fly_zone.update({i: 0})
            for j in temp:
                if i==j:
                    self.non_fly_zone.update({i: temp[j]})

        [self.non_fly_zone.update({i: 0}) if self.non_fly_zone[i]==False else self.non_fly_zone.update({i: 1})
        for i in self.non_fly_zone]
        return self.non_fly_zone

    def demand_constrs(self):
        """
        return customer demand in a sequence of nodes in the weight matrix of the drones and van
        :return: the dictionary of the customer demand
        """
        temp = nx.get_node_attributes(self.route.G, name='demand')  # get a demand of customer nodes, in a length of 14

        for i in self.nodes_oder:
            self.customer_demand.update({i:0})
            for j in temp:
                if i==j:
                    self.customer_demand.update({i: temp[j]})
        return self.customer_demand

    # def dro_connection_constrs(self):
    #     # nx.attr_matrix(self.route.G, edge_attr='weight')
    #     self.dro_connection_matrix = nx.attr_matrix(self.graph, edge_attr='weight', rc_order=self.nodes_oder)
    #     # print(self.dro_connection_matrix)
    #     print("node order of the matrix: ", self.nodes_oder)
    #     return self.dro_connection_matrix

    def weight_matrix_fn(self):
        """
        generate the weight matrix with a form of DataFrame
        :return: the weight of the matrix
        """
        self.weight_matrix = nx.to_pandas_adjacency(self.route.G, nodelist=self.graph.nodes())
        return self.weight_matrix

    def load_rate_matrix_fn(self):
        """
        the matrix of drones and van to effect the left energy and load weight.
        :return: the rate of weight and load for the van and the drone
        """
        shape = len(self.graph.nodes())

        # generate rate matrix of the load and energy for the drone
        temp = np.repeat(1-rate_load_pack_drone, shape*shape)
        self.dro_rate_load_matrix = temp.reshape([shape, shape])

        # generate rate matrix of the load and energy for the drone
        temp = np.repeat(1-rate_load_pack_van, shape*shape)
        self.van_rate_load_matrix = temp.reshape([shape, shape])

        return self.dro_rate_load_matrix, self.van_rate_load_matrix

    # generate solution matrix
    def adjacency_matrix(self):
        """
        adjacency matrix of the graph
        :return: connection matrix of the nodes
        """
        self.weight_matrix_fn()
        # initiate the adjacency matrix
        self.adj_matrix = self.weight_matrix
        for i in self.weight_matrix.index:
            for j in self.weight_matrix.columns:
                if self.weight_matrix.at[i, j] != 0.0:
                    self.adj_matrix.at[i, j] = 1
        # [print(self.adj_matrix.at[self.adj_matrix.index[i], self.adj_matrix.index[j]] == self.adj_matrix.at[self.adj_matrix.index[j], self.adj_matrix.index[i]])
        #  for i in range(len(self.adj_matrix)) for j in range(len(self.adj_matrix))]  # whether the matrix is symmetric or not
        return self.adj_matrix

    def get_intersection_dro_van(self, solution_matrix_van, solution_matrix_drones):
        """
        the intersection nodes that are covered by both drone and van
        :param solution_matrix_van: the matrix of van
        :param solution_matrix_drones: the list of matrixes for drones
        :return: the list of intersection nodes for the drone and van
        """
        intersection_matrix: list = list()
        for n in range(drones_num_on_van):  # there are at least two drones in the network
            # whether the drone and van have covered the same node
            c = [1 for i in range(a.shape[0]) for j in range(a.shape[1])
                 if solution_matrix_van[i, j] == solution_matrix_drones[n][i, j] and a[i,j] == 1]
            intersection_matrix.append(c)

        # sum the number of intersection nodes between (drone_1 and van, drone_2 and van)
        [self.intersection_numbers.append(sum(i)) for i in intersection_matrix]
        return intersection_matrix

    def generate_solution_matrix(self):
        """
        generate the solution matrix of the drones and van
        :return: a list: [solution matrix for the van, solution matrixes for the drones on the van]
        """
        shape = len(self.graph.nodes())
        self.solution_matrix_van = np.zeros([shape, shape])
        [self.solution_matrix_drones.append(np.zeros([shape, shape])) for i in range(drones_num_on_van)]

        return self.solution_matrix_van, self.solution_matrix_drones


initial_solution = GRB_Var_Constrs()
#initial_solution.plot_graph_Weight(r'G:\Unterricht\05-2021\Ipad_Sharing\MA\Routing\8th\map_graph.png')
# ---initiate the related parameters to generate solution matrices
# initial_solution.weight_matrix_fn()
# ------generate matrix randomly
a, b = initial_solution.generate_solution_matrix()
adj_matrix = initial_solution.adjacency_matrix()
# print(adj_matrix.shape, '\n', adj_matrix)
# initial_solution.weights_adj_matrix()
initial_solution.non_fly_zone_constrs()
initial_solution.load_rate_matrix_fn()
initial_solution.get_intersection_dro_van()
