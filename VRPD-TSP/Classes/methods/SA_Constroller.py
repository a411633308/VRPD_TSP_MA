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
import networkx as nx
from random import choice
from Classes.PARAMs import fixed_cost
import gurobipy as gp
import random

from Classes.Customers import Customers
import numpy as np
import copy
import json
import datetime
import time

class SA_Controller:
    def __init__(self):
        self.grb_var: GRB_Var_Constrs = GRB_Var_Constrs()
        self.vehicle: Vehicles = Vehicles()
        self.sa_model: SA_Model = SA_Model(self.grb_var.solution_matrix_drones)

        # ------------ Coefficiency ------------------------------------------------------------------------------------
        # ------------ (1) Costs according to the Routes' Distance ------------------------------------------------------
        temp = list(self.grb_var.graph.edges.data('detour_risks'))
        self.dict_detour: dict = {(i,j): cost for i,j,cost in temp}

        self.graph_data: list = list(self.grb_var.graph.edges.data("weight"))
        self.dict_weight: dict = {(i,j): distance for i,j,distance in self.graph_data}
        self.dict_dro: dict = {(i,j): distance*rate_load_pack_drone*(1+self.grb_var.weather.wind_speed)
                                      +self.dict_detour[i,j]
                               for i,j,distance in self.graph_data}
        self.dict_van: dict = {(i,j): distance*rate_load_pack_van for i,j,distance in self.graph_data}

        # ------------ Variables ---------------------------------------------------------------------------------------
        self.var_van: dict = {(i, j):0 for i,j,distance in self.graph_data}
        self.var_dro: list[dict] = list()
        [self.var_dro.append({(i,j):0 for i,j,distance in self.graph_data}) for n in range(drones_num_on_van)]
        self.vars: dict = {'van': self.var_van, 'dros': self.var_dro}
        self.initial_solution()
        # self.sol_dict: dict = {
        #     0: self.initial_solution,
        #     # 1: self.permutation_solution,
        #     2: self.other_new_generation,
        # }
        self.chosen_routes: dict = dict()
        self.chosen_vars: dict = dict()

        # ------------ (2) Customer Demand -----------------------------------------------------------------------------
        # Customer demand: print(self.grb_var.customer_demand)
        # Customer in "Non fly Zone": print(self.grb_var.non_fly_zone)

        # ------------ Objective ---------------------------------------------------------------------------------------
        self.obj: list = list()
        self.bst_obj: float = self.initial_obj()
        self.bst_sol: dict = {'van': self.vars['van'], 'dros': self.vars['dros']}
        self.shortest_pathes: dict = {'van': 0, 'dro_0':0, 'dor_1':0}

        # ------------ Constrains ---------------r-----------------------------------------------------------------------
        self.dro_constrains: list[Drone_Constrains] = [Drone_Constrains(self.vehicle.drones[i]) for i in range(drones_num_on_van)]
        self.dockhubs_constrains: list[DockingHub_Constrains] = [DockingHub_Constrains(self.grb_var.route.nodes_docking_hubs[i])
                                                                 for i in range(dockhub_num)]
        self.depot_constrain: Depot_Constrains = Depot_Constrains()


    def initial_obj(self):
        self.obj.append(fixed_cost)
        for i, j in list(self.vars['van'].keys()):
            # for x, y in list(self.var_van.keys()):
            if i!=j:
                temp = self.vars['dros'][0][i, j]* \
                       self.dict_dro[i, j] + \
                       self.vars['dros'][1][i, j]* \
                       self.dict_dro[i, j] \
                       + self.var_van[i, j]* \
                       self.dict_van[i, j]
                self.obj.append(temp)
        return sum(self.obj)

    def objective_fn(self):
        """
        the weight_van*solution_van + weight_dro*solution_dro[0] + weight_dro*solution_dro[1] + fixed_cost
        :return: the current best objective
        """
        # the cost for detour the risks area

        self.obj.append(fixed_cost)
        for i, j in list(self.vars['van'].keys()):
            # for x, y in list(self.var_van.keys()):
            if i!=j:
                temp = self.vars['dros'][0][i, j]*\
                       self.dict_dro[i, j] + \
                       self.vars['dros'][1][i, j]*\
                       self.dict_dro[i, j]\
                     + self.vars['van'][i, j]*\
                       self.dict_van[i, j]+\
                       self.dict_detour[i, j]
                self.obj.append(temp)

        if self.bst_obj<=sum(self.obj) and self.bst_obj!=0:
            return self.bst_obj
        elif self.bst_obj>=sum(self.obj):
            # update the best objective result and the related solution
            self.bst_obj=sum(self.obj)

            for i in self.obj:
                self.bst_obj+=i

            self.bst_sol['van'] = self.vars['van']
            self.bst_sol['dros'] = self.vars['dros']
            return self.bst_obj

    # @nb.jit(nopython=True)
    def initial_solution(self):
        """
        generate the initial solution randomly
        :return:
        """
        a = random.choice(range(int(len(self.var_van)/3),int(len(self.var_van)/2)))
        given_list_van = random.sample(range(len(list(self.var_van.keys()))), a)
        given_list_dro: list = [random.sample(range(len(list(self.var_van.keys()))), a) for i in range(drones_num_on_van)]

        for i in range(len(list(self.var_van.keys()))):
            self.var_van[list(self.var_van.keys())[i]] = 1
            if i in given_list_van:
                self.var_van[list(self.var_van.keys())[i]] = random.choice([0,1])

        for n in range(len(given_list_dro)):
            for i in range(len(list(self.var_dro[n].keys()))):
                self.var_dro[n][list(self.var_dro[n].keys())[i]] = 1
                if i in given_list_dro[n]:
                    self.var_dro[n][list(self.var_dro[n].keys())[i]] = random.choice([0,1])

        # ------------ Check the Customer Demand Constrains before SA Model --------------------------------------------
        # collect all connectivities of each customer nodes
        tem: dict = dict()

        for i in list(self.var_dro[0].keys()):
            if i[0][:3]=='cus' or i[1][:3]=='cus':
                tem[i]=self.var_van[i]+self.var_dro[0][i]+self.var_dro[1][i]
        # ------------ the Routes Number Connected to Customer Nodes ---------------------------------------------------

        cus_index: list = [i.index for i in self.grb_var.route.nodes_customers]
        a: dict = {i:0 for i in cus_index}
        for i in cus_index:
            for x,y in tem:
                if (i == x or i == y) and tem[x,y]!=0:
                    a[i] += 1
        cus_demand = {i: self.grb_var.route.find_node(i).pack_needs for i in cus_index}
        # ------------ Check the State of Whether all Customers are surved ---------------------------------------------
        # print("length of costomer nodes for served and overall: ", len(a), len(cus_index))
        cus_demand_total = sum(cus_demand.values())
        if sum(a.values())==sum(cus_demand.values()):
            # self.vars = {'van': self.var_van, 'dros': self.var_dro}
            self.sa_model.set_current_state({'van': self.var_van, 'dros': self.var_dro})

        else:
            b = list(set(cus_index).difference(set(a))) # the customers who are currently unavailable
            if len(b)==len([]):
                self.sa_model.set_current_state({'van': self.var_van, 'dros': self.var_dro})
            else:
                for i,j in list(self.var_dro[1].keys()):
                    # print(j)
                    for n in b:
                        if i==n or j==n:
                            c = np.random.choice([self.var_dro[0],self.var_dro[1],self.var_van])
                            x = c[i,j]
                            c[i,j] = 1
                            y = c[i,j]
                # self.vars = {'van': self.var_van, 'dros': self.var_dro}
                self.sa_model.set_current_state({'van': self.var_van, 'dros': self.var_dro})

    # @nb.jit(nopython=True)
    def constr_valid_solution(self):
        """
        From depot to Docking hubs or depots, the drones does not go alone
        :return: if the current solution is invalid, return False directly, otherwise check multiple object
        """
        # ------------ Valid Solution Judgement ------------------------------------------------------------------------
        index = list(self.var_van.keys())
        for i in range(len(index)):
                # depot -> dock/depot must not be covered by the van
                if index[i][0][:3] == 'dep' and index[i][1][:3] != 'cus':
                    # if the current solution of drones contains the related routes, then generate a new solution.
                    if self.vars['dros'][0][index[i][0], index[i][1]] == 1 or self.vars['dros'][1][index[i][0], index[i][1]]:
                        for n in range(drones_num_on_van):
                            self.vars['dros'][n].update({index[i]: 0})
                        self.vars['van'].update({index[i]: 1})
                        continue

                elif index[i][0][:3] == 'dep' or index[i][1][:3] == 'dep':
                    self.vars['van'].update({index[i]: 1})
                    continue
                elif index[i][0][:3] != 'cus' and index[i][1][:3] == 'cus':
                    for n in range(drones_num_on_van):
                        self.vars['dros'][n].update({index[i]: 1})
                    continue
                elif index[i][1][:3] != 'cus' and index[i][0][:3] == 'cus':
                    for n in range(drones_num_on_van):
                        self.vars['dros'][n].update({index[i]: 1})
                    continue

        return True


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
                index2: list = index.pop(i)
                for j in index2:
                    if index[i][0] == j[0] and index[i][1] != j[1]:
                        temp += 1
                # print('*'*10, ' routes ', j, ' covered times: ', temp, '*'*10)
                if self.grb_var.customer_demand[index[i][0]]!=0 and temp==0:
                    a = choice([self.vars['van'], self.vars['dros'][0], self.vars['dros'][1]])
                    a.update({index[i]: 1})
                    return True
                else:
                    continue
        return True

    def subtour(self, edges):
        """
        find the shortest route
        :param edges: given edges of certain vehicles
        :return:
        """
        unvisited = copy.deepcopy(self.grb_var.nodes_oder)
        cycle = copy.deepcopy(self.grb_var.nodes_oder) # Dummy - guaranteed to be replaced
        while unvisited:  # true if list is non-empty
            thiscycle = []
            neighbors = unvisited
            while neighbors:
                current = neighbors[0]
                thiscycle.append(current)
                unvisited.remove(current)
                neighbors = [j for i, j in edges.select(current, '*')
                             if j in unvisited]
            if len(thiscycle) >= len(cycle) and len(thiscycle)<=self.grb_var.nodes_len:
                cycle = thiscycle # New shortest subtour


        # unvisited_nodes = copy.deepcopy(self.grb_var.nodes_oder)
        # cycle = copy.deepcopy(self.grb_var.nodes_oder)
        # for i in range(len(edges)):
        #     current = unvisited_nodes[0]
        #     thiscycle.append(current)
        #     unvisited_nodes.remove(current)
        #     neighbors = unvisited_nodes
        #     while neighbors:
        #         current = neighbors[0]
        #         thiscycle.append(current)
        #         unvisited.remove(current)
        #         neighbors = [j for i, j in edges.select(current, '*')
        #                      if j in unvisited]
        return cycle

    def constr_connectivity(self):

        # ------------ constrains the length of found subset of the routesz
        flag_van: bool = False
        flag_dro: list[bool] = [False for i in range(drones_num_on_van)]

        edges = gp.tuplelist((i,j) for i,j in self.vars['van'].keys() if self.vars['van'][i,j]!=0)
        cycle1 = self.subtour(edges)

        if len(cycle1)==self.grb_var.nodes_len:
            flag_van=True
            self.chosen_routes['van'] = cycle1


        # chosen_routes_dros: list = list()
        chosen_nodes_dros: list = list()
        for n in range(drones_num_on_van):
            edges = gp.tuplelist(i for i,j in self.var_dro[n].items() if j!=0)

            cycle1 = self.subtour(edges)
            if len(cycle1)>=int(self.grb_var.nodes_len/2):
                flag_dro[n] = True
                chosen_nodes_dros.append(cycle1)
                self.shortest_pathes['dro_'+str(n)] = cycle1

        flag = (flag_dro.count(True)==2)
        del(flag_dro)
        if flag == flag_van == True:
            self.chosen_routes['dros'] = chosen_nodes_dros
            # self.chosen_vars['dros'] = chosen_routes_dros
            [self.vars['van'].update({(i,j): 0}) for i,j in list(self.var_van.keys())]
            [self.vars['van'].update({(x, y):1})
             for i in self.chosen_routes['van']
             for x,y in list(self.var_van.keys()) if (x==i and y!=i) or (x!=i and y==i)]
            # self.vars['van'] = {t.update({(x, y):1})
            #                     for i in self.chosen_routes['van']
            #                     for x,y in list(self.var_van.keys()) if x==i or y==i}
            for n in range(drones_num_on_van):

                self.vars['dros'][n] = {(i, j): 0 for i, j in list(self.var_dro[n].keys())}
                [self.vars['dros'][n].update({(x, y):1}) for i in self.chosen_routes['dros'][n]
                for x,y in list(self.var_van.keys()) if (x==i and y!=i) or (x!=i and y==i)]

            if self.chosen_routes['van'][0][:3]=='dep' and self.chosen_routes['van'][-1][:3]=='dep' and \
                    self.chosen_routes['dros'][0][-1][:3]!='cus' and self.chosen_routes['dros'][1][-1][:3]!='cus':
                return True
            else:
                return False
        else:
            return False
    #
    # def conjunction_van_dock(self):
    #     """
    #     the conjunction of van and the docking hubs
    #     :return: the conjunction number
    #     """
    #     index = list(self.vars['van'].keys())
    #     conj_num: int = 0
    #     for i in range(len(index)):
    #         if index[i][0] == 'doc' or index[i][1]=='doc':
    #             conj_num += 1
    #     return conj_num

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
        index: list = list(self.vars['van'])
        conj_num: dict = dict()
        from Classes.PARAMs import drones_num_on_van
        for n in range(drones_num_on_van):
            tem: int = 0
            for i in range(len(index)):
                if self.vars['van'][index[i]] == self.vars['dros'][n][index[i]] == 1:
                    tem += 1
            conj_num.update({'dros'+str(n): tem})

        # print("found conjunction of van and dro are: ", conj_num)
        return conj_num

    def constr_max_packages(self):
        """
        constrains for the van and dros
        :return:
        """
        possible: int = self.conjunction_with_str('doc', self.vars['van'])*max_pack_num_van
        actual: int = self.conjunction_with_str('cus', self.vars['van'])
        possible0: int = self.conjunction_with_str('doc', self.vars['dros'][0])*max_pack_num_dro
        actual0: int = self.conjunction_with_str('cus',self.vars['dros'][0])
        possible1: int = self.conjunction_with_str('doc', self.vars['dros'][1])*max_pack_num_dro
        actual1: int = self.conjunction_with_str('cus',self.vars['dros'][1])
        if actual<=possible and actual0<=possible0 and actual1<=possible1:
            return True
        else:
            return False

    def constr_energy_dro(self):
        index: list = list(self.dict_van.keys())
        used_fuel = [self.vars['van'][index[i]]*self.dict_van[index[i]] for i in range(len(index))]
        flag: list = list()

        available_batteries: dict = dict()
        for n in range(drones_num_on_van):
            available_batteries.update({'dros'+str(n): self.conjunction_with_str('doc', self.vars['dros'][n]) +
                                                       self.conjunction_van_dro()['dros'+str(n)]})

        flag.append(sum(used_fuel) <= max_range_van*self.conjunction_with_str('doc', self.vars['van']))
        used_batteries: dict = dict()
        for n in range(drones_num_on_van):
            used_batteries['dros'+str(n)] = [self.vars['dros'][n][index[i]]*self.dict_van[index[i]]+self.dict_detour[index[i]]
                                             for i in range(len(index))]
            flag.append(sum(used_batteries['dros'+str(n)]) <= flying_range_drone*available_batteries['dros'+str(n)])

            # print("energy control: ", available_batteries['dros'+str(n)]*max_range_van, '\n', sum(used_batteries['dros'+str(n)]))
        # print("flag of energy control: ", flag)
        return flag.count(True) == drones_num_on_van+1

    def recurse_evaluation(self):
        # import sys
        # sys.setrecursionlimit(1000000)
        flag = False

        judge: dict = dict()
        # [judge.update({'valid':self.constr_valid_solution()}) for i in range(1000000) if judge['valid']==False]
        # [judge.update({'demand':self.constr_req_demand()}) if judge['demand']==False else break for i in range(1000000)]

        for i in range(10000000000000):
            self.initial_solution()
            # print('-'*10, ' round ', i,' ', '-'*10)
            judge['valid'] = self.constr_valid_solution()
            # print('*'*10, ' check the connectivity of the van. ')
            judge['non_fly'] = self.constr_non_fly_zone()
            # print('*'*10, ' check the non flying zone of the drones. ')
            # print('*'*10, ' check the validity of the van with drones. ')
            judge['demand'] = self.constr_req_demand()
            # print('*'*10, ' check the customer demand. ')
            judge['van_conn'] = self.constr_connectivity()
            judge['pack'] = self.constr_max_packages()
            # print('*'*10, ' check the packages requirment. ')
            judge['ener_dro'] = self.constr_energy_dro()
            # print('*'*10, ' check the energy constrains of the drone . ')
            # print(judge)
            if judge['non_fly']==False or judge['valid']==False or judge['van_conn']==False \
                    or judge['pack']==False or judge['ener_dro']==False:
                # if i%1000==0:
                #     print(judge['non_fly'], judge['valid'], judge['van_conn'],
                #          judge['pack'], judge['ener_dro'])
                #     print('='*10, '> tried 1000 solutions')
                continue
            else:
                return True

    def invalid_Sol(self):
        return "invalid solution"

    # @nb.jit(nopython=True)
    # def permutation_solution(self):
    #     """
    #     Exchange the connectivity of some routes of the drones and van matrixes
    #     :return: the new solution that has mutated
    #     """
    #     # print('*'*10, ' New Solution through Permutation 1 ', '*'*10)
    #     list_van_1: list = list(self.var_van.keys())
    #     list_van_2: list = np.random.permutation(list_van_1)
    #     list_van_2: list = [(i,j) for i,j in list_van_2]
    #     list_van_3: list = np.random.permutation(list_van_2)
    #     list_van_3: list = [(i,j) for i,j in list_van_3]
    #
    #     list_dro0_1: list = list(self.var_dro[0].keys())
    #     print(list_dro0_1)
    #     list_dro0_2: list = np.random.permutation(list_dro0_1)
    #     list_dro0_2: list = [(i,j) for i,j in list_dro0_2]
    #     list_dro0_3: list = np.random.permutation(list_dro0_2)
    #     list_dro0_3: list = [(i,j) for i,j in list_dro0_3]
    #     list_dro1_1: list = list(self.var_dro[1].keys())
    #     list_dro1_2: list = np.random.permutation(list_dro1_1)
    #     list_dro1_2: list = [(i,j) for i,j in list_dro1_2]
    #     list_dro1_3: list = np.random.permutation(list_dro1_2)
    #     list_dro1_3: list = [(i,j) for i,j in list_dro1_3]
    #
    #     for i in range(len(list_van_2)):
    #         self.var_van[list_van_1[i]] = np.random.choice([self.vars['van'][list_van_1[i]],
    #                                                         self.vars['van'][list_van_2[i]],
    #                                                         self.vars['van'][list_van_3[i]]])
    #         self.var_dro[0][list_dro0_1[i]] = np.random.choice([self.var_dro[0][list_dro0_1[i]],
    #                                                             self.var_dro[0][list_dro0_2[i]],
    #                                                             self.var_dro[0][list_dro0_3[i]]])
    #         self.var_dro[1][list_dro1_1[i]] = np.random.choice([self.var_dro[1][list_dro1_1[i]],
    #                                                             self.var_dro[1][list_dro1_2[i]],
    #                                                             self.var_dro[1][list_dro1_3[i]]])
    #     self.vars = {'van': self.var_van, 'dros': self.var_dro}
    #     return self.vars

    # @nb.jit
    # def other_new_generation(self):
    #     # print('*'*10, ' New Solution through Permutation2  ', '*'*10)
    #     index = list(self.var_van.keys())
    #     for i in range(len(self.var_van)):
    #         temp = 0
    #         a = np.random.choice(range(len(self.var_van)))
    #         temp = self.var_van[index[i]]
    #         self.var_van[index[i]] = self.var_van[index[a]]
    #         self.var_van[index[a]] = temp
    #         temp = 0
    #         temp = self.var_dro[0][index[i]]
    #         self.var_dro[0][index[i]] = self.var_dro[0][index[a]]
    #         self.var_dro[0][index[a]] = temp
    #         temp = 0
    #         temp = self.var_dro[1][index[i]]
    #         self.var_dro[1][index[i]] = self.var_dro[1][index[a]]
    #         self.var_dro[1][index[a]] = temp
    #
    #     self.vars = {'van': self.var_van, 'dros': self.var_dro}
    #     return self.vars

    # @nb.vectorize(nonpython=True)
    # def new_solution(self, i: int):
    #     fun = self.sol_dict.get(i, self.invalid_Sol)
    #     return fun()

    def sa_optimize_fn(self):
        start_time = time.time()
        for i in range(int((self.sa_model.initial_temp-self.sa_model.final_temp)/self.sa_model.alpha)):
        # for i in range(2):
        #     if i == 0:
        #         print('*'*10, ' log ', i, ' ', '*'*10)
        #         self.initial_solution()
        #         self.sa_model.initial_state = self.vars
        #         self.sa_model.current_state = self.sa_model.initial_state
        #         self.recurse_evaluation()
        #         print('*'*10, ' recurse ', '*'*10)
        #         self.objective_fn()
        #         print('*'*10, ' objective function ', '*'*10)
        #         self.sa_model.change_current_temp()
        #         continue
        #     else:
        #     print('*'*10, ' log ', i, ' ', '*'*10)
            self.initial_solution()
            self.recurse_evaluation()
            # print('*'*10, ' recurse ', '*'*10)
            self.objective_fn()
            # print('*'*10, ' objective function ', '*'*10)
            self.sa_model.change_current_temp()
            continue

        # print('*'*10, ' The best Solution ', self.obj,'\n',
        #       self.bst_obj, '*'*10)
        # print("best solution for the van: ", self.bst_sol['van'])
        # print("shortest path for the vehicles: ", self.shortest_pathes['van'],'\n', self.shortest_pathes['dro_0'],'\n',
        #       self.shortest_pathes['dro_1'])
        # for n in range(drones_num_on_van):
        #     print("\nbest solution for the drone", n , self.bst_sol['dros'][n])

        end_time = time.time()
        json_dict: dict = {
            'best objective list': self.obj,
            'best value of objective ': self.bst_obj,
            'shortest path': self.bst_sol,
            'time costs': (end_time-start_time)/60
        }
        dateArray = datetime.datetime.utcfromtimestamp(time.time())
        otherStyleTime = dateArray.strftime("%m%d")
        result_path = './../../Results/dep_'+str(depot_num)+'_doc'+str(dockhub_num)+'_cus'+str(customer_num)+'_'+\
                      str(otherStyleTime)+'.json'
        self.save_to_json(json_dict, result_path)

        return self.bst_obj

    def save_to_json(self, data_dict: dict, url: str):
        fileObject = open(url, 'w')
        for obj in data_dict.items():
            fileObject.write(str(obj))
            fileObject.write('\n')
        fileObject.close()

sa_controller = SA_Controller()
sa_controller.sa_optimize_fn()
# sa_controller.constr_energy_dro()
# sa_controller.constr_connectivity()