#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.Routes import Routes
import random

import networkx as nx
import numpy as np
from pandas import DataFrame
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
        self.solution_matrix_drones: list[DataFrame] = list()
        self.solution_matrix_van: DataFrame = None

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
        self.battery_intersections: list = list()

        # ------------ initiation of variables and constrains ----------------------------
        self.weight_matrix_fn()
        self.generate_solution_matrix()
        self.non_fly_zone_constrs()
        self.demand_constrs()
        self.load_rate_matrix_fn()
        self.adjacency_matrix()
        self.get_battery_backup(self.solution_matrix_van, self.solution_matrix_drones)

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

    def non_fly_zone_constrs(self): # not in the same oder as self.nodes_order
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

    def demand_constrs(self):  # not in the same oder as self.nodes_order
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
        self.dro_rate_load_matrix = DataFrame(temp.reshape([shape, shape]), columns=self.nodes_oder, index=self.nodes_oder)

        # generate rate matrix of the load and energy for the drone
        temp = np.repeat(1-rate_load_pack_van, shape*shape)
        self.van_rate_load_matrix = DataFrame(temp.reshape([shape, shape]), columns=self.nodes_oder, index=self.nodes_oder)

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

    def get_battery_backup(self, solution_matrix_van, solution_matrix_drones):
        """
        1. the intersection nodes that are covered by both drone and van
        2. the routes that contains a docking hub node that are covered by drones
        :param solution_matrix_van: the matrix of van
        :param solution_matrix_drones: the list of matrixes for drones
        :return: the list of intersection nodes for the drone and van
        """
        # ------------ battery backup from van -------------------------------------------
        intersection_matrix: list = list()
        a: list = list()
        b: list = list()

        for n in range(drones_num_on_van):  # there are at least two drones in the network
            # whether the drone and van have covered the same node
            c = [1 if solution_matrix_van.at[i, j] == solution_matrix_drones[n].at[i, j] and solution_matrix_van.at[i,j] == 1
                 else 0 for i in solution_matrix_van.index for j in solution_matrix_van.columns]

            # for j in solution_matrix_van.index:
            #     for i in solution_matrix_van.columns:
            #         if solution_matrix_van.at[i, j] == solution_matrix_drones[n].at[i, j] and solution_matrix_van.at[i, j] == 1:
            #             print(1)
                    #print("van solution: \n", solution_matrix_van.at[i, j], "\n drone solution: \n", solution_matrix_drones[n].at[i, j])

            intersection_matrix.append(c)

        # sum the number of intersection nodes between (drone_1 and van, drone_2 and van)
        [a.append(sum(i)) for i in intersection_matrix]

        # ------------ battery backup from docking hubs -----------------------------------
        # ------------ adjacency matrix that is only related to docking hubs --------------
        d = self.adj_matrix # initiation matrix that
        for i in self.adj_matrix.index:
            for j in self.adj_matrix.columns:
                if self.adj_matrix.at[i, j] == 1 and (i[:3] == "doc" or j[:3] == "doc"):
                    d.at[i, j] = 1
                else:
                    d.at[i, j] = 0

        intersection_matrix: list = list()
        for n in range(drones_num_on_van):  # there are at least two drones in the network
            # whether the drone and van have covered the same node
            c = [1 if d.at[i, j] == solution_matrix_drones[n].at[i, j] and d.at[i,j] == 1
                 else 0 for i in d.index for j in d.columns]

            intersection_matrix.append(c)

        # sum the number of intersection nodes between (drone_1 and van, drone_2 and van)
        [b.append(sum(i)) for i in intersection_matrix]

        intersection_matrix: list = list()
        [intersection_matrix.append(a[i] + b[i]) for i in range(len(a))]

        self.battery_intersections = sum(intersection_matrix)
        return intersection_matrix

    # def get_package_backup(self):

    def generate_solution_matrix(self):
        """
        generate the solution matrix of the drones and van
        :return: a list: [solution matrix for the van, solution matrixes for the drones on the van]
        """
        import pandas as pd
        shape = len(self.graph.nodes())
        self.solution_matrix_van = pd.DataFrame(np.zeros([shape, shape]), columns=self.nodes_oder, index=self.nodes_oder)
        [self.solution_matrix_drones.append(pd.DataFrame(np.zeros([shape, shape]), columns=self.nodes_oder, index=self.nodes_oder))
         for i in range(drones_num_on_van)]
        return self.solution_matrix_van, self.solution_matrix_drones


initial_solution = GRB_Var_Constrs()
