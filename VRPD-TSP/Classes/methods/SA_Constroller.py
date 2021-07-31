#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.methods.SA_Model import SA_Model
from Classes.methods.Station_Constrains import Depot_Constrains, DockingHub_Constrains
from Classes.methods.Drone_Constrains import Drone_Constrains
from Classes.methods.GRB_Var_Constrs import GRB_Var_Constrs
from Classes.PARAMs import drones_num_on_van, dockhub_num, rate_load_pack_drone, rate_load_pack_van
from Classes.Vehicles import Vehicles
import numba as nb
import networkx as nx
from random import choice
from Classes.PARAMs import fixed_cost

from Classes.Customers import Customers
import numpy as np

class SA_Controller:
    def __init__(self):
        self.grb_var: GRB_Var_Constrs = GRB_Var_Constrs()
        self.vehicle: Vehicles = Vehicles()
        self.sa_model: SA_Model = SA_Model(self.grb_var.solution_matrix_drones)
        # print(type(self.solution_van))


        # ------------ Coefficiency ------------------------------------------------------------------------------------
        # ------------ (1) Weight --------------------------------------------------------------------------------------
        self.graph_data: list = list(self.grb_var.graph.edges.data("weight"))
        self.dict_weight: dict = {(i,j): distance for i,j,distance in self.graph_data}
        self.dict_dro: dict = {(i,j): distance*rate_load_pack_drone for i,j,distance in self.graph_data}
        self.dict_van: dict = {(i,j): distance*rate_load_pack_van for i,j,distance in self.graph_data}

        # ------------ Variables ---------------------------------------------------------------------------------------
        self.var_van: dict = {(i, j):0 for i,j,distance in self.graph_data}
        self.var_dro: list[dict] = list()
        [self.var_dro.append({(i,j):0 for i,j,distance in self.graph_data}) for n in range(drones_num_on_van)]
        self.vars: dict = {'van': self.var_van, 'dros': self.var_dro}
        self.sol_dict: dict = {
            0: self.initial_solution,
            1: self.permutation_solution,
            2: self.other_new_generation,
        }

        # ------------ (2) Customer Demand -----------------------------------------------------------------------------
        # Customer demand: print(self.grb_var.customer_demand)
        # Customer in "Non fly Zone": print(self.grb_var.non_fly_zone)

        # ------------ Objective ---------------------------------------------------------------------------------------
        self.obj: list = list()
        self.bst_obj: float = sum(self.obj)
        self.bst_sol: dict = {'van': self.var_van, 'dros': self.var_dro}
        self.shortest_pathes: dict = {'van': 0, 'dro_0':0, 'dor_1':0}

        # ------------ Constrains ---------------r-----------------------------------------------------------------------
        self.dro_constrains: list[Drone_Constrains] = [Drone_Constrains(self.vehicle.drones[i]) for i in range(drones_num_on_van)]
        self.dockhubs_constrains: list[DockingHub_Constrains] = [DockingHub_Constrains(self.grb_var.route.nodes_docking_hubs[i])
                                                                 for i in range(dockhub_num)]
        self.depot_constrain: Depot_Constrains = Depot_Constrains()

    # @nb.jit(nopython=True)
    def objective_fn(self):
        """
        the weight_van*solution_van + weight_dro*solution_dro[0] + weight_dro*solution_dro[1] + fixed_cost
        :return: the current best objective
        """
        self.obj.append(fixed_cost)
        for i, j in list(self.var_van.keys()):
            # for x, y in list(self.var_van.keys()):
            if i!=j:
                temp = self.var_dro[0][i, j]*\
                       self.dict_dro[i, j] + \
                       self.var_dro[0][i, j]*\
                       self.dict_dro[i, j]\
                     + self.var_van[i, j]*\
                       self.dict_van[i, j]
                self.obj.append(temp)

        if self.bst_obj<=sum(self.obj):
            return self.bst_obj
        elif self.bst_obj>=sum(self.obj):
            # update the best objective result and the related solution
            self.bst_obj = sum(self.obj)
            self.bst_sol['van'] = self.var_van
            self.bst_sol['dros'] = self.var_dro
            return self.bst_obj

    # @nb.jit(nopython=True)
    def initial_solution(self):
        """
        generate the initial solution randomly
        :return:
        """
        # print('*'*10, ' New Solution Randomly ', '*'*10)
        # print("======> before ", self.var_van)
        # [self.var_van.update({i: choice([0,1])}) for i in list(self.var_van.keys())]
        for i in list(self.var_van.keys()):
            self.var_van[i] = np.random.choice([0,1])
        # print("======> after ", self.var_van)
        # [self.var_dro[n].update({i: choice([0,1])}) for n in range(drones_num_on_van) for i in list(self.var_dro[n].keys())]
        for n in range(drones_num_on_van):
            for i in list(self.var_dro[n].keys()):
                self.var_dro[n][i] = choice([0,1])

        # ------------ Check the Customer Demand Constrains before SA Model --------------------------------------------
        # collect all connectivities of each customer nodes
        tem: dict = dict()
        # [tem.update({i: self.var_van[i]+self.var_dro[0][i]+self.var_dro[1][i]})
        #  for i in self.var_dro[0] if i[0][:3]=='cus' or i[1][:3]=='cus']
        for i in self.var_dro[0]:
            if i[0][:3]=='cus' or i[1][:3]=='cus':
                tem[i]=self.var_van[i]+self.var_dro[0][i]+self.var_dro[1][i]
        # ------------ the Routes Number Connected to Customer Nodes ---------------------------------------------------
        # cus_index: list = list()
        # for i in self.grb_var.route.nodes_customers:
        #     cus_index.append(i)
        cus_index: list = [i.index for i in self.grb_var.route.nodes_customers]

        a: dict = dict()
        for i in cus_index:
            for x,y in tem:
                if (i == x or i == y) and tem[x,y]!=0:
                    a[i] = 1

        # ------------ Check the State of Whether all Customers are surved ---------------------------------------------
        # print("length of costomer nodes for served and overall: ", len(a), len(cus_index))
        if len(a)==len(cus_index):
            # print("*"*10 + ' Generate a Set of Solution Randomly' +"*"*10)
            self.vars = {'van': self.var_van, 'dros': self.var_dro}
            self.sa_model.set_current_state(self.vars)

        else:
            b = list(set(cus_index).difference(set(a))) # the customers who are currently unavailable
            for i,j in self.var_dro[0]:
                for n in b:
                    if i==n or j==n:
                        c = np.random.choice([self.var_dro[0],self.var_dro[1],self.var_van])
                        x = c[i,j]
                        c[i,j] = 1
                        y = c[i,j]
                        # print("*"*10 + ' Generate another Set of Solution Randomly' +"*"*10)
            self.vars = {'van': self.var_van, 'dros': self.var_dro}
            self.sa_model.set_current_state(self.vars)

    # @nb.jit(nopython=True)
    def constr_valid_solution(self):
        """
        :return: if the current solution is invalid, return False directly, otherwise check multiple object
        """
        # ------------ Valid Solution Judgement ------------------------------------------------------------------------
        index = list(self.var_van.keys())
        for i in range(len(index)):
                # depot -> dock/depot must not be covered by the van
                if index[i][0][:3] == 'dep' and (index[i][1][:3] == 'dep' or index[i][1][:3] == 'doc'):
                    # if the current solution of drones contains the related routes, then generate a new solution.
                    if self.vars['dros'][0][index[i][0], index[i][1]] == 1 or self.vars['dros'][1][index[i][0], index[i][1]]:
                        self.new_solution(np.random.choice(range(3)))
                        # print('*'*10, ' Generates new solution', '*'*10)
                        return False

                elif index[i][0][:3] == 'dep' and index[i][1][:3] == 'cus':
                    # print('*'*10, ' Valid Solution for the Drones and Van', '*'*10)
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
                        # should generate a new set of solution matrixes
                        self.new_solution(np.random.choice(range(3)))
                        return False
                    else:
                        return True
                elif type(y_node) == type(Customers()) and type(x_node) != type(Customers()):
                    if y_node.in_non_flying == 1:
                        # should generate a new set of solution matrixes
                        self.new_solution(np.random.choice(range(3)))
                        return False
                    else:
                        return True
                elif type(y_node) == type(Customers()) and type(x_node) == type(Customers()):
                    if x_node.in_non_flying == 1 or y_node.in_non_flying == 1:
                        self.new_solution(np.random.choice(range(3)))
                        return False
                    else:
                        return True

    # @nb.jit(nopython=True)
    def constr_req_demand(self):
        index = list(self.var_van.keys())
        for i in range(len(index)):
                temp = 0
                for j,h in set(index)-set(index[i]):
                    if index[i][0] == j and index[i][1] != h:
                        temp += 1
                # print('*'*10, ' routes ', j, ' covered times: ', temp, '*'*10)
                if self.grb_var.customer_demand[index[i][0]]!=0 and temp==0:
                    self.new_solution(np.random.choice(range(3)))
                    # print('*'*10, ' Unsatisfied Customer Demand ', '*'*10)
                    return False
                else:
                    continue
        return True
        # ------------ Customer Demand Constrains ----------------------------------------------------------------------

        # ------------ Energy Constrains -------------------------------------------------------------------------------
        # ------------

        # ------------ Non Flying Zone Constrains ----------------------------------------------------------------------

        # ------------ Packages Reload ---------------------------------------------------------------------------------
        # print('************ (7) ')
    def constr_connectivity_van(self):
        a = nx.from_edgelist(self.vars['van'])
        solution_matrix = nx.to_numpy_array(a)
        # print(solution_matrix)
        depot_index = [i for i in range(self.grb_var.nodes_len) if self.grb_var.nodes_oder[i][:3]=='dep']
        target_index = [-i for i in range(self.grb_var.nodes_len) if sum(solution_matrix[-i])!=0]
        matrix = nx.shortest_path(a, source=self.grb_var.nodes_oder[depot_index[0]], target=self.grb_var.nodes_oder[target_index[0]])
        # print('\n =====> shortest path lengtsh: ', nx.shortest_path_length(a, source=self.grb_var.nodes_oder[depot_index[0]]))
        # print(type(matrix),'\n', matrix)
        if len(matrix)==1:
            self.new_solution(np.random.choice(range(3)))
            return False
        elif len(matrix) == self.grb_var.nodes_len:
            self.shortest_pathes['van'] = matrix
            return True
        else:
            self.new_solution(np.random.choice(range(3)))
            return False

    def constr_connectivity_dros(self, str, var):
        a = nx.from_edgelist(var)
        # b = nx.from_edgelist(self.vars['dros'][0])

        solution_matrix = nx.to_numpy_array(a)
        # print(solution_matrix)
        depot_index = [i for i in range(self.grb_var.nodes_len) if self.grb_var.nodes_oder[i][:3]=='dep']
        target_index = [-i for i in range(self.grb_var.nodes_len) if sum(solution_matrix[-i])!=0]
        matrix = nx.shortest_path(a, source=self.grb_var.nodes_oder[depot_index[0]], target=self.grb_var.nodes_oder[target_index[0]])
        # print('\n =====> shortest path lengtsh: ', nx.shortest_path_length(a, source=self.grb_var.nodes_oder[depot_index[0]]))
        # print(type(matrix),'\n', matrix)
        if len(matrix)==1:
            self.new_solution(np.random.choice(range(3)))
            return False
        elif len(matrix) == self.grb_var.nodes_len:
            self.shortest_pathes[str] = matrix
            return True
        else:
            self.new_solution(np.random.choice(range(3)))
            return False
        #     b = nx.from_dict_of_lists(matrix)
        #     c = nx.to_numpy_array(b)
        # print('------> \n', matrix,'\n******>\n', c)

    # def shortest_path(self, input_matrix):

    # @nb.jit(nopython=True)
    def recurse_evaluation(self):
        # import sys
        # sys.setrecursionlimit(1000000)
        flag = False

        judge: dict = {'valid': False, 'demand': False, 'van_conn': False, 'dro_0': False, 'dro_1': False}
        # [judge.update({'valid':self.constr_valid_solution()}) for i in range(1000000) if judge['valid']==False]
        # [judge.update({'demand':self.constr_req_demand()}) if judge['demand']==False else break for i in range(1000000)]

        for i in range(10000000000000):
            judge['non_fly'] = self.constr_non_fly_zone()
            judge['valid'] = self.constr_valid_solution()
            judge['van_conn'] = self.constr_connectivity_van()
            judge['dro_0'] = self.constr_connectivity_dros('dro_0', self.vars['dros'][0])
            judge['dro_1'] = self.constr_connectivity_dros('dro_1', self.vars['dros'][1])
            if judge['non_fly']==False or judge['valid']==False or judge['van_conn']==False \
                    or judge['dro_0']==False or judge['dro_1']==False:
                continue
            else:
                flag = True
                break
        #
        # for i in range(1000000):
        #     judge['valid'] = self.constr_valid_solution()
        #     if judge['valid']==False:
        #         continue
        #     else:
        #         flag2 = True
        #         break
        #
        # for i in range(100000000):
        #     judge['van_conn'] = self.constr_connectivity()
        #     if judge['van_conn']==False:
        #         continue
        #     else:
        #         flag3 = True
        #         break
        print(flag)
        return flag

    def invalid_Sol(self):
        return "invalid solution"

    # @nb.jit(nopython=True)
    def permutation_solution(self):
        """
        Exchange the connectivity of some routes of the drones and van matrixes
        :return: the new solution that has mutated
        """
        # print('*'*10, ' New Solution through Permutation 1 ', '*'*10)
        list_van_1: list = list(self.var_van.keys())
        list_van_2: list = np.random.permutation(list_van_1)
        list_van_2: list = [(i,j) for i,j in list_van_2]
        list_van_3: list = np.random.permutation(list_van_2)
        list_van_3: list = [(i,j) for i,j in list_van_3]

        list_dro0_1: list = list(self.var_dro[0].keys())
        list_dro0_2: list = np.random.permutation(list_dro0_1)
        list_dro0_2: list = [(i,j) for i,j in list_dro0_2]
        list_dro0_3: list = np.random.permutation(list_dro0_2)
        list_dro0_3: list = [(i,j) for i,j in list_dro0_3]
        list_dro1_1: list = list(self.var_dro[1].keys())
        list_dro1_2: list = np.random.permutation(list_dro1_1)
        list_dro1_2: list = [(i,j) for i,j in list_dro1_2]
        list_dro1_3: list = np.random.permutation(list_dro1_2)
        list_dro1_3: list = [(i,j) for i,j in list_dro1_3]

        for i in range(len(list_van_2)):
            self.var_van[list_van_1[i]] = np.random.choice([self.vars['van'][list_van_1[i]],
                                                            self.vars['van'][list_van_2[i]],
                                                            self.vars['van'][list_van_3[i]]])
            self.var_dro[0][list_dro0_1[i]] = np.random.choice([self.vars['van'][list_dro0_1[i]],
                                                                self.vars['van'][list_dro0_2[i]],
                                                                self.vars['van'][list_dro0_3[i]]])
            self.var_dro[1][list_dro1_1[i]] = np.random.choice([self.vars['van'][list_dro1_1[i]],
                                                                self.vars['van'][list_dro1_2[i]],
                                                                self.vars['van'][list_dro1_3[i]]])
        self.vars = {'van': self.var_van, 'dros': self.var_dro}
        return self.vars

    # @nb.jit
    def other_new_generation(self):
        # print('*'*10, ' New Solution through Permutation2  ', '*'*10)
        index = list(self.var_van.keys())
        for i in range(len(self.var_van)):
            temp = 0
            a = np.random.choice(range(len(self.var_van)))
            temp = self.var_van[index[i]]
            self.var_van[index[i]] = self.var_van[index[a]]
            self.var_van[index[a]] = temp
            temp = 0
            temp = self.var_dro[0][index[i]]
            self.var_dro[0][index[i]] = self.var_dro[0][index[a]]
            self.var_dro[0][index[a]] = temp
            temp = 0
            temp = self.var_dro[1][index[i]]
            self.var_dro[1][index[i]] = self.var_dro[1][index[a]]
            self.var_dro[1][index[a]] = temp

        self.vars = {'van': self.var_van, 'dros': self.var_dro}
        return self.vars

    # @nb.vectorize(nonpython=True)
    def new_solution(self, i: int):
        fun = self.sol_dict.get(i, self.invalid_Sol)
        return fun()

    def sa_optimize_fn(self):
        self.initial_solution()
        self.sa_model.initial_state = self.vars
        self.sa_model.current_state = self.sa_model.initial_state
        print(self.sa_model.current_temp, self.sa_model.final_temp)
        if self.sa_model.current_temp>=self.sa_model.final_temp:
            print(1)
            self.recurse_evaluation()
            print(2)
            self.objective_fn()
            print(3)
            self.sa_model.change_current_temp()
            print(4)
        else:
            print('*'*10, ' finish the Optimization Process ', '*'*10)
            return

sa_controller = SA_Controller()
sa_controller.initial_solution()
sa_controller.sa_optimize_fn()