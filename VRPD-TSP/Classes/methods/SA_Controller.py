#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.methods.SA_Model import SA_Model
from Classes.methods.Station_Constrains import Depot_Constrains, DockingHub_Constrains
from Classes.methods.Drone_Constrains import Drone_Constrains
from Classes.methods.GRB_Var_Constrs import GRB_Var_Constrs
from Classes.PARAMs import drones_num_on_van, dockhub_num, rate_load_pack_drone, rate_load_pack_van
from Classes.PARAMs import max_pack_num_van
from Classes.PARAMs import max_pack_num_dro, max_range_van, flying_range_drone, dockhub_num, depot_num, customer_num
from Classes.Vehicles import Vehicles
import numba as nb

import sys
import networkx as nx
from random import choice
from Classes.PARAMs import fixed_cost
import gurobipy as gp
import random
import matplotlib.pyplot as plt
from Classes.PARAMs import seed_num

from Classes.Customers import Customers
from Classes.Log_Model import JasonLog
import numpy as np
import copy
import datetime
import time
import os

sys.setrecursionlimit(999999999)


class SA_Controller:
    def __init__(self):
        self.grb_var: GRB_Var_Constrs = GRB_Var_Constrs()
        self.vehicle: Vehicles = Vehicles()
        self.sa_model: SA_Model = SA_Model(self.grb_var.solution_matrix_drones)
        dateArray = datetime.datetime.utcfromtimestamp(time.time())
        otherStyleTime = dateArray.strftime("%m%d")
        path = r"G:\Unterricht\05-2021\MA\Projects\VRPD-TSP\Results\logs\dep" + str(depot_num) + "_doc" + str(
            dockhub_num) + "_cus" + str(customer_num)  # log path
        path_result = r"G:\Unterricht\05-2021\MA\Projects\VRPD-TSP\Results\Models\dep" + str(depot_num) + "_doc" + str(
            dockhub_num) + "_cus" + str(customer_num)  # result path
        self.log_json: JasonLog = JasonLog(log_url=path, result_url=path_result)

        # ------------ Original Graph Data -----------------------------------------------------------------------------

        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
        self.grb_var.plot_graph_weight(path + "/" + str(otherStyleTime) + "original_graph.png")

        # ------------ Coefficiency ------------------------------------------------------------------------------------
        # ------------ (1) Costs according to the Routes' Distance ------------------------------------------------------
        temp = list(self.grb_var.graph.edges.data('detour_risks'))
        self.dict_detour: dict = {(i, j): cost for i, j, cost in temp}

        self.graph_data: list = list(self.grb_var.graph.edges.data("weight"))
        self.dict_weight: dict = {(i, j): distance for i, j, distance in self.graph_data}
        self.dict_dro: dict = {(i, j): distance * rate_load_pack_drone * (1 + self.grb_var.weather.wind_speed)
                                       + self.dict_detour[i, j]
                               for i, j, distance in self.graph_data}
        self.dict_van: dict = {(i, j): distance * rate_load_pack_van for i, j, distance in self.graph_data}

        # ------------ Variables ---------------------------------------------------------------------------------------
        self.var_van: dict = {(i, j): 0 for i, j, distance in self.graph_data}  # chosen routes by van
        self.var_dro: list[dict] = list()  # chosen route by drones
        [self.var_dro.append({(i, j): 0 for i, j, distance in self.graph_data}) for n in range(drones_num_on_van)]
        self.van_path: list = list()
        self.dros_path: list = [list() for i in range(drones_num_on_van)]
        self.vars: dict = {'van': self.var_van, 'dros': self.var_dro}

        # ------------ the path according to the variables -------------------------------------------------------------
        # self.initial_solution()
        self.chosen_routes: dict = dict()
        self.chosen_vars: dict = dict()
        # ------------ (2) Customer Demand -----------------------------------------------------------------------------
        # Customer demand: print(self.grb_var.customer_demand)
        # Customer in "Non fly Zone": print(self.grb_var.non_fly_zone)

        # ------------ Objective ---------------------------------------------------------------------------------------
        self.obj: list = list()
        self.bst_obj: float = self.initial_obj()
        self.bst_sol: dict = {'van': self.vars['van'], 'dros': self.vars['dros']}
        self.shortest_pathes: dict = {'van': 0, 'dro_0': 0, 'dor_1': 0}
        self.cur_obj: float = 0.0

        # ------------ Constrains ---------------r-----------------------------------------------------------------------
        # self.dro_constrains: list[Drone_Constrains] = [Drone_Constrains(self.vehicle.drones[i]) for i in range(drones_num_on_van)]
        # self.dockhubs_constrains: list[DockingHub_Constrains] = [DockingHub_Constrains(self.grb_var.route.nodes_docking_hubs[i])
        #                                                          for i in range(dockhub_num)]
        # self.depot_constrain: Depot_Constrains = Depot_Constrains()

    # find the proper routes marked in dictionary
    def find_proper_value(self, index: tuple, dic: dict):
        """
        :param index: index of chosen routes from variables generated randomly
        :param dic: {(node1_index, node2_index): weight, ......}
        :return: the value of the given routes in the giben dictionary
        """
        if index in dic:
            return dic[index]
        elif (index[1], index[0]) in dic:
            return dic[(index[1], index[0])]

    def initial_obj(self):
        self.obj = []
        self.obj.append(fixed_cost)
        self.obj.append(sum([self.find_proper_value((i,j), self.var_van)*self.find_proper_value((i,j), self.dict_van)
                         for i, j in list(self.var_van.keys()) ]))
        self.obj.append(
            sum([
            sum([self.find_proper_value((i, j), self.var_dro[n])*self.find_proper_value((i,j), self.dict_dro)
                 for i, j in list(self.var_dro[n].keys())])
                    for n in range(drones_num_on_van)])
        )
        return sum(self.obj)

    def objective_fn(self):
        """
        the weight_van*solution_van + weight_dro*solution_dro[0] + weight_dro*solution_dro[1] + fixed_cost
        :return: the current best objective
        """
        self.cur_obj = self.initial_obj()

        if self.bst_obj <= self.cur_obj and self.bst_obj != 300:
            return self.bst_obj
        elif self.bst_obj > self.cur_obj or self.bst_obj == 300:
            # update the best objective result and the related solution
            self.bst_obj = self.cur_obj
            self.bst_sol['van'] = self.var_van
            self.bst_sol['dros'] = self.var_dro

            return self.bst_obj

    # # @nb.jit(nopython=True)
    # def initial_solution(self):
    #     """
    #     generate the initial solution randomly
    #     :return:
    #     """
    #     a = random.choice(range(int(len(self.var_van) / 3), int(len(self.var_van) / 2)))
    #     given_list_van = random.sample(range(len(list(self.var_van.keys()))), a)
    #     given_list_dro: list = [random.sample(range(len(list(self.var_van.keys()))), a) for i in
    #                             range(drones_num_on_van)]
    #
    #     for i in range(len(list(self.var_van.keys()))):
    #         self.var_van[list(self.var_van.keys())[i]] = 1
    #         if i in given_list_van:
    #             self.var_van[list(self.var_van.keys())[i]] = random.choice([0, 1])
    #
    #     for n in range(len(given_list_dro)):
    #         for i in range(len(list(self.var_dro[n].keys()))):
    #             self.var_dro[n][list(self.var_dro[n].keys())[i]] = 1
    #             if i in given_list_dro[n]:
    #                 self.var_dro[n][list(self.var_dro[n].keys())[i]] = random.choice([0, 1])
    #
    #     # ------------ Check the Customer Demand Constrains before SA Model --------------------------------------------
    #     # collect all connectivities of each customer nodes
    #     tem: dict = dict()
    #
    #     for i in list(self.var_dro[0].keys()):
    #         if i[0][:3] == 'cus' or i[1][:3] == 'cus':
    #             tem[i] = self.var_van[i] + self.var_dro[0][i] + self.var_dro[1][i]
    #     # ------------ the Routes Number Connected to Customer Nodes ---------------------------------------------------
    #
    #     cus_index: list = [i.index for i in self.grb_var.route.nodes_customers]
    #     a: dict = {i: 0 for i in cus_index}
    #     for i in cus_index:
    #         for x, y in tem:
    #             if (i == x or i == y) and tem[x, y] != 0:
    #                 a[i] += 1
    #     cus_demand = {i: self.grb_var.route.find_node(i).pack_needs for i in cus_index}
    #     # ------------ Check the State of Whether all Customers are surved ---------------------------------------------
    #     # print("length of costomer nodes for served and overall: ", len(a), len(cus_index))
    #     cus_demand_total = sum(cus_demand.values())
    #     if sum(a.values()) == sum(cus_demand.values()):
    #         # self.vars = {'van': self.var_van, 'dros': self.var_dro}
    #         self.sa_model.set_current_state({'van': self.var_van, 'dros': self.var_dro})
    #
    #     else:
    #         b = list(set(cus_index).difference(set(a)))  # the customers who are currently unavailable
    #         if len(b) == len([]):
    #             self.sa_model.set_current_state({'van': self.var_van, 'dros': self.var_dro})
    #         else:
    #             for i, j in list(self.var_dro[1].keys()):
    #                 # print(j)
    #                 for n in b:
    #                     if i == n or j == n:
    #                         c = np.random.choice([self.var_dro[0], self.var_dro[1], self.var_van])
    #                         x = c[i, j]
    #                         c[i, j] = 1
    #                         y = c[i, j]
    #             # self.vars = {'van': self.var_van, 'dros': self.var_dro}
    #             self.sa_model.set_current_state({'van': self.var_van, 'dros': self.var_dro})

    # # @nb.jit(nopython=True)
    # def constr_valid_solution(self):
    #     """
    #     From depot to Docking hubs or depots, the drones does not go alone
    #     :return: if the current solution is invalid, return False directly, otherwise check multiple object
    #     """
    #     # ------------ Valid Solution Judgement ------------------------------------------------------------------------
    #     index = list(self.var_van.keys())
    #     for i in range(len(index)):
    #             # depot -> dock/depot must not be covered by the van
    #             if index[i][0][:3] == 'dep' and index[i][1][:3] != 'cus':
    #                 # if the current solution of drones contains the related routes, then generate a new solution.
    #                 if self.vars['dros'][0][index[i][0], index[i][1]] == 1 or self.vars['dros'][1][index[i][0], index[i][1]]:
    #                     for n in range(drones_num_on_van):
    #                         self.vars['dros'][n].update({index[i]: 0})
    #                     self.vars['van'].update({index[i]: 1})
    #                     continue
    #
    #             elif index[i][0][:3] == 'dep' or index[i][1][:3] == 'dep':
    #                 self.vars['van'].update({index[i]: 1})
    #                 continue
    #             elif index[i][0][:3] != 'cus' and index[i][1][:3] == 'cus':
    #                 for n in range(drones_num_on_van):
    #                     self.vars['dros'][n].update({index[i]: 1})
    #                 continue
    #             elif index[i][1][:3] != 'cus' and index[i][0][:3] == 'cus':
    #                 for n in range(drones_num_on_van):
    #                     self.vars['dros'][n].update({index[i]: 1})
    #                 continue
    #
    #     return True

    # @nb.jit(nopython=True)
    def constr_non_fly_zone(self):
        index = list(self.var_van.keys())
        for i in range(len(index)):
            if index[i][0][:3] == 'cus' or index[i][1][:3] == 'cus':
                x_node = self.grb_var.route.find_node(index[i][0])
                y_node = self.grb_var.route.find_node(index[i][1])
                if type(x_node) == type(Customers()) and type(y_node) != type(Customers()):
                    if x_node.in_non_flying == 1:
                        self.vars['dros'][0].update({index[i]: 0})
                        self.vars['dros'][1].update({index[i]: 0})
                        continue
                    else:
                        continue
                elif type(y_node) == type(Customers()) and type(x_node) != type(Customers()):
                    if y_node.in_non_flying == 1:
                        # should generate a new set of solution matrixes
                        self.vars['dros'][0].update({index[i]: 0})
                        self.vars['dros'][1].update({index[i]: 0})
                        continue
                    else:
                        continue
                elif type(y_node) == type(Customers()) and type(x_node) == type(Customers()):
                    if x_node.in_non_flying == 1 or y_node.in_non_flying == 1:
                        self.vars['dros'][0].update({index[i]: 0})
                        self.vars['dros'][1].update({index[i]: 0})
                        continue
                    else:
                        continue
        return True

    # @nb.jit(nopython=True)
    def constr_req_demand(self):
        index = list(self.var_van.keys())

        for i in range(len(index)):
            temp = 0
            index2 = copy.deepcopy(index)
            # print("!!!"*10, i, ' ', len(index))
            index2: list = index2.pop(i)
            for j in index2:
                if index[i][0] == j[0] and index[i][1] != j[1]:
                    temp += 1
            # print('*'*10, ' routes ', j, ' covered times: ', temp, '*'*10)
            if self.grb_var.customer_demand[index[i][0]] != 0 and temp == 0:
                a = choice([self.vars['van'], self.vars['dros'][0], self.vars['dros'][1]])
                a.update({index[i]: 1})
                return True
            else:
                continue
        return True

    # def subtour(self, edges):
    #     """
    #     find the shortest route
    #     :param edges: given edges of certain vehicles
    #     :return:
    #     """
    #     # print("related edges", edges)
    #     a = list()
    #     [a.extend([i, j]) for i, j in edges]
    #     b = list(set(a))
    #     b.sort(key=a.index)
    #     # print("unique nodes of the edges: ", len(b), self.grb_var.nodes_len)
    #     unvisited = copy.deepcopy(b)
    #     cycle = copy.deepcopy(b)  # Dummy - guaranteed to be replaced
    #     while unvisited:  # true if list is non-empty
    #         thiscycle = []
    #         neighbors = unvisited
    #         while neighbors:
    #             current = neighbors[0]
    #             thiscycle.append(current)
    #             unvisited.remove(current)
    #             neighbors = [j for i, j in edges.select(current, '*')
    #                          if j in unvisited]
    #         if len(thiscycle) >= len(cycle) and len(thiscycle) <= self.grb_var.nodes_len:
    #             cycle = thiscycle  # New shortest subtour
    #
    #     # print("found cycle:\n", cycle)
    #     return cycle

    # def plot_graph(self, graph, graph_url):
    #     plt.rcParams['figure.figsize'] = (10, 10)
    #     plt.rcParams['font.size'] = 15
    #     plt.title('Chosen Route of van')
    #     pos = nx.spring_layout(self.grb_var.route.G, seed=seed_num)
    #     # nx.draw(self.G, node_color=self.grb_var.route.color_map, with_labels=True, node_size=1200, font_size=25)
    #
    #     path = "./../../Results/logs/"
    #     # nx.draw_spectral(self.grb_var.route.G, edgelist=self.bst_sol['van'].keys(),
    #     #                  node_color=self.grb_var.route.color_map, edge_color='skyblue')
    #     # plt.savefig(path+"/"+graph_url+'van.jpg')
    #     nx.draw(graph, pos=pos, node_color=self.grb_var.route.color_map, edge_color='orange')
    #     # plt.savefig(path+"/"+graph_url+'dro0.png')
    #     # nx.draw_spectral(self.grb_var.route.G,  edgelist=self.bst_sol['dros'][1].keys(),
    #     #                  node_color=self.grb_var.route.color_map, edge_color='tomato')
    #     # plt.savefig(path+"/"+graph_url+'dro1.jpg')
    #     plt.show()

    # def related_routes(self, found_routes: list):
    #     found_routes2 = list()
    #     for i in range(len(found_routes) - 1):
    #         for a, b in found_routes[i]:
    #             temp = list()
    #             for x, y in found_routes[i + 1]:
    #                 # print(x, y)
    #                 if x == b or x == a or y == b or y == a:
    #                     temp.append((a, b))
    #                     break
    #             found_routes2.append(temp)
    #     return [random.choice(i) for i in found_routes2]

    def related_routes(self, path_list):
        b = list()
        for i in range(len(path_list) - 1):
            # print(path_list[i], path_list[i+1])
            a = self.grb_var.graph.edges(path_list[i])
            for x, y in a:
                if y == path_list[i + 1]:
                    b.append((x, y))
        return b

    def random_walk_van(self):
        # the van path should be larger or equal to the node length.
        random_path = nx.generate_random_paths(self.grb_var.route.G, sample_size=1,
                                               path_length=self.grb_var.nodes_len - 1)
        path_list = list(random_path)[0]
        # ensure start from a depot and end to a depot
        flag_list = [i[:3] == 'dep' for i in path_list]
        if len(path_list) == 0:
            return False
        elif flag_list[0] == flag_list[-1] == True and flag_list[1:-1].count(False) == len(flag_list[1:-1]):
            b = self.related_routes(path_list)
            # initial the variable for the van
            var: dict = {i: 0 for i in b}
            for i in b:
                var[i] += 1

            self.van_path = path_list
            self.var_van = var
            return True
        else:
            return False

    def random_walk_dro(self, j=None):
        # the van path should be larger or equal to the node length.
        random_path = nx.generate_random_paths(self.grb_var.route.G, sample_size=2,
                                               path_length=self.grb_var.nodes_len - 1)
        path_list: list = list(random_path)
        flag_list = [[i[:3] == 'dep' for i in path_list[j]] for j in range(drones_num_on_van)]

        if [len(path_list[i]) for i in range(drones_num_on_van)].count(0) == 2:
            return False
        # flag_list[i][0]==flag_list[i][-1]==True
        elif [flag_list[i][0]==True for i in range(drones_num_on_van)].count(True)==2 and \
             [flag_list[i][1:-1].count(False)==len(flag_list[i][1:-1]) for i in range(drones_num_on_van)].count(True)==2:
            b: list = [self.related_routes(path_list[i]) for i in range(drones_num_on_van)]
            var: list[dict] = [{i: 0 for i in b[i]} for i in range(drones_num_on_van)]
            for n in range(drones_num_on_van):
                a = list()
                for i in b[n]:
                    var[n][i] += 1
            # print(len(path_list[0]), len(path_list[1]))
            self.dros_path = path_list
            self.var_dro = var
            return True
        else:
            return False

    def initial_solution_NX(self):
        for i in range(100000000000000000):
            judge: dict = dict()
            judge['van'] = self.random_walk_van()
            judge['dros'] = self.random_walk_dro()
            if judge['van']==True and judge['dros']==True:
                print(judge)
                self.vars = {'van': self.var_van, 'dros': self.var_dro}
                break
            else:
                continue

    # if len(path_list)==0:
    #     self.van_random_walk()
    # elif path_list[0][:3]=='dep' and path_list[-1][:3]=='dep':
    #     found_routes = [self.grb_var.graph.edges(i) for i in path_list]
    #     # [print(i) for i in found_routes]
    #     found_routes2 = list()
    #     for i in range(len(found_routes)-1):
    #         for a,b in found_routes[i]:
    #             temp = list()
    #             for x,y in found_routes[i+1]:
    #                 print(x, y)
    #                 if x==b or x==a or y==b or y==a:
    #                     temp.append((a,b))
    #             found_routes2.append(temp)
    #     # [print(i) for i in found_routes2]
    #     chosen_routes = [random.choice(i) for i in found_routes2]
    #     # print(type(self.bst_sol['van'].keys()),'\n', chosen_routes)
    #     G_van_solution = nx.from_edgelist(chosen_routes)
    #     self.plot_graph(G_van_solution, 'ssdfsdo')
    # else:
    #     self.van_random_walk()

    # nx.edge_disjoint_paths()
    # nx.parse_edgelist()

    # def constr_connectivity(self):
    #
    #     # ------------ constrains the length of found subset of the routesz
    #     flag_van: bool = False
    #     flag_dro: list[bool] = [False for i in range(drones_num_on_van)]
    #
    #     edges = gp.tuplelist((i, j) for i, j in self.vars['van'].keys() if self.vars['van'][i, j] != 0)
    #     cycle1 = self.subtour(edges)
    #     # path = nx.generate_random_paths(self.grb_var.route.G, path_length=self.grb_var.nodes_len)
    #     # cycle1 = nx.shortest_path(self.grb_var.route.G, source=self.grb_var.route.nodes_depot[0].index,
    #     #                            target=self.grb_var.route.nodes_depot[-1].index)
    #     # print(path)
    #     if len(cycle1) == self.grb_var.nodes_len:
    #         flag_van = True
    #         self.chosen_routes['van'] = cycle1
    #         # print("the found path of van:", cycle1)
    #
    #     chosen_nodes_dros: list = list()
    #     for n in range(drones_num_on_van):
    #         edges = gp.tuplelist(i for i, j in self.var_dro[n].items() if j != 0)
    #
    #         cycle1 = self.subtour(edges)
    #         if len(cycle1) >= int(self.grb_var.nodes_len / 2):
    #             flag_dro[n] = True
    #             chosen_nodes_dros.append(cycle1)
    #             self.shortest_pathes['dro_' + str(n)] = cycle1
    #
    #     flag = (flag_dro.count(True) == 2)
    #     del (flag_dro)
    #     if flag == flag_van == True:
    #         self.chosen_routes['dros'] = chosen_nodes_dros
    #         # self.chosen_vars['dros'] = chosen_routes_dros
    #         [self.vars['van'].update({(i, j): 0}) for i, j in list(self.var_van.keys())]
    #         [self.vars['van'].update({(x, y): 1})
    #          for i in self.chosen_routes['van']
    #          for x, y in list(self.var_van.keys()) if (x == i and y != i) or (x != i and y == i)]
    #         # self.vars['van'] = {t.update({(x, y):1})
    #         #                     for i in self.chosen_routes['van']
    #         #                     for x,y in list(self.var_van.keys()) if x==i or y==i}
    #         for n in range(drones_num_on_van):
    #             self.vars['dros'][n] = {(i, j): 0 for i, j in list(self.var_dro[n].keys())}
    #             [self.vars['dros'][n].update({(x, y): 1}) for i in self.chosen_routes['dros'][n]
    #              for x, y in list(self.var_van.keys()) if (x == i and y != i) or (x != i and y == i)]
    #
    #         if self.chosen_routes['van'][0][:3] == 'dep' and self.chosen_routes['van'][-1][:3] == 'dep' and \
    #                 self.chosen_routes['dros'][0][-1][:3] != 'cus' and self.chosen_routes['dros'][1][-1][:3] != 'cus':
    #             return True
    #         else:
    #             return False
    #     else:
    #         return False

    def conjunction_with_str(self, st: str, input: dict):
        """
        the conjunction of van or drones with the customer nodes
        :param input: the tupledict of the vehicle
        :return: the conjunction number
        """
        index = list(input.keys())
        conj_num: int = 0
        for i in range(len(index)):
            if index[i][0][:3] == st or index[i][1][:3] == st:
                conj_num += 1
        return conj_num

    def conjunction_van_dro(self):
        """
        find the conjunction of drones with the van
        :return: the dict of conjunction of drones with the van
        """
        index: list = list(self.var_van)
        conj_num: list = list()

        for n in range(drones_num_on_van):
            tem: int = 0
            for i in range(len(index)):
                # if self.var_dro[n][index[i]] == self.var_dro[n][index[i]] == 1:
                if self.find_proper_value(index[i], self.var_dro[n]) == self.find_proper_value(index[i],
                                                                                                 self.var_van):
                    tem += 1
            conj_num.append(tem)

        return conj_num

    def constr_max_packages(self):
        """
        constrains for the van and dros
        :return:
        """
        possible: int = self.conjunction_with_str('doc', self.vars['van']) * max_pack_num_van
        actual: int = self.conjunction_with_str('cus', self.vars['van'])
        possible0: int = self.conjunction_with_str('doc', self.vars['dros'][0]) * max_pack_num_dro
        actual0: int = self.conjunction_with_str('cus', self.vars['dros'][0])
        possible1: int = self.conjunction_with_str('doc', self.vars['dros'][1]) * max_pack_num_dro
        actual1: int = self.conjunction_with_str('cus', self.vars['dros'][1])
        # print(actual,possible,actual0,possible0,actual1,possible1)
        if actual <= possible and int(actual0 / 2) <= possible0 and int(actual1 / 2) <= possible1:
            return True
        else:
            return False


    def constr_energy_dro(self):

        # ------------ energy constraints for the van ------------------------------------------------------------------
        index_van: list = list(self.var_van.keys())
        # used_fuel: list = list()
        # for i in range(len(index_van)):
        #     used_fuel.append(self.var_van[index_van[i]] * self.find_proper_value(index_van[i], self.dict_van))
        used_fuel = [self.var_van[index_van[i]] * self.find_proper_value(index_van[i], self.dict_van)
                     for i in range(len(index_van))]
        flag: list = list()
        flag.append(sum(used_fuel) <= max_range_van * self.conjunction_with_str('doc', self.vars['van']))

        # ------------ energy constraints for the dros -----------------------------------------------------------------
        # available_batteries: list = list()
        # for n in range(drones_num_on_van):
        #     available_batteries.append(self.conjunction_with_str('doc', self.vars['dros'][n]) + self.conjunction_van_dro()[n])
        available_batteries = [self.conjunction_with_str('doc', self.vars['dros'][n]) + self.conjunction_van_dro()[n]
                               for n in range(drones_num_on_van) ]

        used_batteries: list = list()
        for n in range(drones_num_on_van):
            index_dros: list = list(self.vars['dros'][n].keys())
            used_batteries.append(
                [self.find_proper_value(index_dros[i], self.var_dro[n])*
                 self.find_proper_value(index_dros[i], self.dict_van)+
                 self.find_proper_value(index_dros[i], self.dict_detour) for i in range(len(index_dros))
                ]
            )
            flag.append(sum(used_batteries[n]) <= flying_range_drone * available_batteries[n])
        return flag.count(True) == drones_num_on_van + 1

    def recurse_evaluation(self):
        flag = False
        judge: dict = dict()
        for i in range(10000000000000):
            # self.initial_solution()
            self.initial_solution_NX()
            # judge["valid"] = self.constr_valid_solution()
            judge["non_fly"] = self.constr_non_fly_zone()
            judge["demand"] = self.constr_req_demand()
            # judge["van_conn"] = self.constr_connectivity()
            judge["pack"] = self.constr_max_packages()  # pay highly attention to a proper values for the max_pack_num_dro and number of docking hub nodes
            judge["ener_dro"] = self.constr_energy_dro()
            print(judge)
            if judge["non_fly"] == False or judge["pack"] == False or judge['ener_dro'] == False:
                self.initial_solution_NX()
                continue
            else:
                self.plot_given_routes(str(time.time())[-5:])
                return True

    def plot_given_routes(self, graph_url):
        plt.rcParams['figure.figsize'] = (40, 40)
        plt.rcParams['font.size'] = 50
        plt.title('Chosen Route of van')
        pos = nx.spring_layout(self.grb_var.route.G, seed=seed_num)
        # nx.draw(self.G, node_color=self.grb_var.route.color_map, with_labels=True, node_size=1200, font_size=25)

        # path = "./../../Results/logs/" + str(depot_num) + "_doc" + str(dockhub_num) + "_cus" + str(customer_num)

        folder = os.path.exists(self.log_json.log_loc)
        if not folder:
            os.makedirs(self.log_json.log_loc)
        else:
            for n in range(drones_num_on_van):
                nx.draw_spectral(self.grb_var.route.G,  edgelist=self.var_dro[n].keys(), # pos=pos,
                                 node_color=self.grb_var.route.color_map, edge_color='orange')
                plt.savefig(self.log_json.log_loc + "\_" + graph_url + 'dro'+str(n)+'.png')

            nx.draw_spectral(self.grb_var.route.G,  edgelist=self.var_van.keys(), # pos=pos,
                             node_color=self.grb_var.route.color_map, edge_color='orange')
            plt.savefig(self.log_json.log_loc + "\\" + graph_url + 'van.png')

            plt.close()

    def sa_optimize_fn(self):
        start_time = time.time()

        # initial a json file to preserve searched solution in each iteration
        self.log_json.initiate_json()

        # ------------------------------- main part of the SA ----------------------------------------------------------
        for i in range(int((self.sa_model.initial_temp - self.sa_model.final_temp) / self.sa_model.alpha)):
            print('*' * 10, ' ', i)
            self.initial_solution_NX()
            # whether the current solution fulfill the constraints
            self.recurse_evaluation()
            # the cost function by the current valid solution
            self.objective_fn()

            # researve the current solution
            json_dict: dict = {
                "the current objective value": self.cur_obj,
                "shortest path": str({'van': len(self.vars['van']), 'dros': [len(self.vars['dros'][0]),
                                                                             len(self.vars['dros'][0])]}),
            }
            log: dict = {i: json_dict}
            self.log_json.append_to_json(log)  # add a new record to the log file

            self.sa_model.change_current_temp()

        end_time = time.time()
        # record the optimal solution by the SA controller
        json_dict: dict = {
            "time costs": (end_time - start_time) / 60,
            "best objective list": self.obj,
            "best value of objective ": self.bst_obj,
            "shortest path": {'van':self.van_path,
                              'dros':self.dros_path},
            "chosen routes": self.vars
        }
        self.log_json.save_to_json(json_dict)

        return self.bst_obj
