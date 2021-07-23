#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.Routes import Routes

import networkx as nx
import numpy as np
from pandas import DataFrame
import matplotlib.pyplot as plt
from Classes.PARAMs import color_list, seed_num, graph_params_list, route_params_list, non_fly_num
from Classes.PARAMs import customer_num, dockhub_num, drones_num_on_van, rate_load_pack_drone, rate_load_pack_van
from Classes.Weather import Weather

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
        # ------------initiate route and graph automatically--------------------------------
        self.route: Routes = Routes(bat_dock_num=self.route_params_list[0], drone_fly_range=self.route_params_list[1],
                                    cust_needs=self.route_params_list[2])
        self.graph = self.route.G
        # set several customers live in a "non flying range."
        self.route.set_non_flying(self.non_flying_num)
        # length of nodes exists in the graph
        self.nodes_len: int = len(self.route.nodes_graph)
        self.nodes_oder = [self.route.nodes_graph[i].index for i in range(len(self.route.nodes_graph))]


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

        # ------------generate weights and related factor matrix of drones ----------------
        self.graph = self.route.G
        self.weight_matrix = nx.attr_matrix(self.route.G, edge_attr='weight', rc_order=self.nodes_oder)  # edge distance
        self.dro_rate_load_matrix: np.matrix = np.zeros([self.nodes_len,self.nodes_len])
        self.van_rate_load_matrix: np.matrix = np.zeros([self.nodes_len,self.nodes_len])
        self.weather: Weather = Weather()
        self.weather_rate_matrix: np.matrix = np.zeros([self.nodes_len, self.nodes_len])
        # ------------ objects for the variables -----------------------------------------
        self.dro_connection_matrix: DataFrame = DataFrame()
        self.van_connection_matrix: DataFrame = DataFrame()

        self.solution_matrix_drones: list = [np.zeros([self.nodes_len,self.nodes_len]) for i in range(drones_num_on_van)]
        self.solution_matrix_van = np.zeros([self.nodes_len, self.nodes_len])

        # ------------ objects for constrains --------------------------------------------
        self.dro_van_connections: list = list()
        self.customer_demand = nx.get_node_attributes(self.route.G, name='demand')
        self.intersection_van_doc_num: int = 0  # the number of intersection nodes between van and docking hubs
        self.intersection_dro_vanDoc_num: int = 0  # the number of intersection nodes between drones and (van and docking hubs)
        self.non_fly_zone: np.matrix = nx.attr_matrix(self.route.G, edge_attr="non_fly_zone", rc_order=self.nodes_oder)

        # ------------ the number of drone and van that have intersections ---------------
        self.battery_intersections: list = list()

        # ------------ initiation of variables and constrains ----------------------------
        # self.plot_graph_weight(r'G:\Unterricht\05-2021\Ipad_Sharing\MA\Routing\8th_Random_Graphs\map_graph_with_weight.png')

        self.adjacency_matrix()
        self.load_rate_matrix_fn()
        self.weather_matrix_fn()

        self.get_battery_backup(self.solution_matrix_van, self.solution_matrix_drones)
        self.get_package_backup(solution_matrix_van=self.solution_matrix_van,
                                solution_matrix_drones=self.solution_matrix_drones)

    def plot_graph_weight(self, graph_url: str):
        """
        plot the graph with van weight as label of the edge
        :param graph_url: the url address to save the iamge
        :return: none
        """
        plt.rcParams['figure.figsize'] = (60, 60)
        plt.rcParams['font.size'] = 55
        plt.title('Map Graph with Weights as Edge Labels')

        node_labels = nx.get_node_attributes(self.route.G, 'type')
        edge_labels = nx.get_edge_attributes(self.route.G, 'weight')

        pos = nx.spring_layout(self.route.G, seed=seed_num)
        nx.draw_networkx_edge_labels(self.route.G, pos, edge_labels=edge_labels, font_size=35)
        nx.draw_networkx_labels(self.route.G, pos, labels=node_labels, font_size=35)
        nx.draw(self.graph, node_color=self.route.color_map, pos=pos, with_labels=False, node_size=1500, font_size=35)

        plt.savefig(graph_url)
        plt.close()


    # def dro_connection_constrs(self):
    #     # nx.attr_matrix(self.route.G, edge_attr='weight')
    #     self.dro_connection_matrix = nx.attr_matrix(self.graph, edge_attr='weight', rc_order=self.nodes_oder)
    #     # print(self.dro_connection_matrix)
    #     print("node order of the matrix: ", self.nodes_oder)
    #     return self.dro_connection_matrix

    def weather_matrix_fn(self):
        """
        the matrix of drones and van to effect the left energy and load weight.
        :return: the rate of weight and load for the van and the drone
        """
        # get the wind direction at each routes, 1: accelerates the drone's flying, -1: decreases the drone's flying
        wind_direction_matrix = nx.attr_matrix(self.route.G, edge_attr='wind_direction', rc_order=self.nodes_oder)

        # generate rate matrix of the weather
        self.weather_rate_matrix = wind_direction_matrix*self.weather.wind_speed + 1
        return self.weather_rate_matrix

    def load_rate_matrix_fn(self):
        """
        the matrix of drones and van to effect the left energy and load weight.
        :return: the rate of weight and load for the van and the drone
        """
        # generate rate matrix of the load and energy for the drone
        if self.adj_matrix is not None:
            self.dro_rate_load_matrix = self.adj_matrix*(1 + rate_load_pack_drone)
            self.van_rate_load_matrix = self.adj_matrix*(1 + rate_load_pack_van)

        return self.dro_rate_load_matrix, self.van_rate_load_matrix

    def adjacency_matrix(self):
        """
        weight matrix and connection of the graph
        :return: connection matrix of the nodes
        """
        # the adjacency matrix of the graph
        self.adj_matrix: bytearray = np.zeros((self.nodes_len, self.nodes_len))
        a = nx.to_numpy_matrix(self.route.G)
        for i in range(len(a)):
            for j in range(len(a)):
                if a[i,j] != 0:
                    self.adj_matrix[i,j] = 1

        return self.adj_matrix

    def get_battery_backup(self, solution_matrix_van, solution_matrix_drones):
        """
        get batteries backup for the drones
        1. the intersection nodes that are covered by both drone and van
        2. the routes that contains a docking hub node that are covered by drones
        :param solution_matrix_van: the matrix of van
        :param solution_matrix_drones: the list of matrixes for drones
        :return: the numbers of drones can change their batteries
        """
        # ------------ battery backup from van -------------------------------------------
        intersection_matrix: list = list()
        a: list = list()
        b: list = list()

        for n in range(drones_num_on_van):  # there are at least two drones in the network
            # whether the drone and van have covered the same node
            c = [1 if solution_matrix_van[i, j] == solution_matrix_drones[n][i, j] and solution_matrix_van[i,j] == 1
                 else 0 for i in range(self.nodes_len) for j in range(self.nodes_len)]

            # for j in solution_matrix_van.index:
            #     for i in solution_matrix_van.columns:
            #         if solution_matrix_van.at[i, j] == solution_matrix_drones[n].at[i, j] and solution_matrix_van.at[i, j] == 1:
            #             print(1)
                    #print("van solution: \n", solution_matrix_van.at[i, j], "\n drone solution: \n", solution_matrix_drones[n].at[i, j])

            intersection_matrix.append(c)

        # sum the number of intersection nodes between (drone_1 and van, drone_2 and van)
        [a.append(sum(i)) for i in intersection_matrix]
        self.dro_van_connections:list = a

        # ------------ battery backup from docking hubs -----------------------------------
        # ------------ adjacency matrix that is only related to docking hubs --------------
        d = self.adj_matrix # initiation matrix that
        for i in range(self.nodes_len):
            for j in range(self.nodes_len):
                if self.adj_matrix[i, j] == 1 and (self.nodes_oder[i][:3] == "doc" or self.nodes_oder[j][:3] == "doc"):
                    d[i, j] = 1
                else:
                    d[i, j] = 0

        intersection_matrix: list = list()
        for n in range(drones_num_on_van):  # there are at least two drones in the network
            # whether the drone and van have covered the same node
            c = [1 if d[i, j] == solution_matrix_drones[n][i, j] and d[i,j] == 1
                 else 0 for i in range(self.nodes_len) for j in range(self.nodes_len)]

            intersection_matrix.append(c)

        # sum the number of intersection nodes between (drone_1 and van, drone_2 and van)
        [b.append(sum(i)) for i in intersection_matrix]

        intersection_matrix: list = list()
        intersection_matrix.append(a)
        intersection_matrix.append(b)

        d: list = list()
        [d.append(a[i] + b[i]) for i in range(len(a))]

        self.battery_intersections = intersection_matrix  # [intersection between van and drones, docking hubs and drones]

        return sum(d)

    def get_package_backup(self, solution_matrix_drones: list, solution_matrix_van):
        """
        get the packages backup for the van(with docking hubs) and drones(with vans and docking hubs)
        :param solution_matrix_drones:
        :param solution_matrix_van:
        :return: self.intersection_van_doc_num * max_pack_van = overall packages the van can deliver
         self.intersection_dro_vanDoc_num * max_pack_dro = overall packages the drones can deliver
        """
        # ------------ adjacency matrix that is only related to docking hubs ---------------------------
        # ------------ d: the adjacency matrix that contains only the connection of docking hub nodes --
        d = self.adj_matrix # initiation matrix that
        for i in range(self.nodes_len):
            for j in range(self.nodes_len):
                if self.adj_matrix[i, j] == 1 and (self.nodes_oder[i][:3] == "doc" or self.nodes_oder[j][:3] == "doc"):
                    d[i, j] = 1
                else:
                    d[i, j] = 0

        # ------------ intersection_matrix: the intersection nodes of drones and the d matrix ----------
        intersection_matrix: list = list()
        for n in range(drones_num_on_van):  # there are at least two drones in the network
            # whether the drone and van have covered the same node
            c = [1 if d[i, j] == solution_matrix_drones[n][i, j] and d[i, j] == 1
                 else 0 for i in range(self.nodes_len) for j in range(self.nodes_len)]

            intersection_matrix.append(c)
        # ------------ a: numbers of intersection nodes for each drones and the d matrix ---------------
        a: list = list()
        [a.append(sum(intersection_matrix[i])) for i in range(len(intersection_matrix))]
        # ------------ b: numbers of intersection nodes for each drones and the van --------------------
        b: list = self.dro_van_connections
        # self.intersection_dro_vanDoc: list = [a, b]
        self.intersection_dro_vanDoc_num: int = sum([sum(a), sum(b)])
        # ------------ b: numbers of intersection nodes for van and the d matrix -----------------------
        c = [1 if d[i, j] == solution_matrix_van[i, j] and d[i, j] == 1
             else 0 for i in range(self.nodes_len) for j in range(self.nodes_len)]
        self.intersection_van_doc_num: int = sum(c)
        return self.intersection_van_doc_num, self.intersection_dro_vanDoc_num


bd = GRB_Var_Constrs()