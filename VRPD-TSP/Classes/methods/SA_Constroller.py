#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.methods.SA_Model import SA_Model
from Classes.methods.Station_Constrains import Depot_Constrains, DockingHub_Constrains
from Classes.methods.Drone_Constrains import Drone_Constrains
from Classes.methods.GRB_Var_Constrs import GRB_Var_Constrs
from Classes.PARAMs import drones_num_on_van, dockhub_num, rate_load_pack_drone, rate_load_pack_van
from Classes.Vehicles import Vehicles

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
            1: self.mutate_solution,
            2: self.other_new_generation,
        }

        # ------------ (2) Customer Demand -----------------------------------------------------------------------------
        # Customer demand: print(self.grb_var.customer_demand)
        # Customer in "Non fly Zone": print(self.grb_var.non_fly_zone)

        # ------------ Objective ---------------------------------------------------------------------------------------
        self.obj: float = 0.0
        self.bst_obj: float = self.obj
        self.bst_sol: dict = {'van': self.var_van, 'dros': self.var_dro}

        # ------------ Constrains --------------------------------------------------------------------------------------
        self.dro_constrains: list[Drone_Constrains] = [Drone_Constrains(self.vehicle.drones[i]) for i in range(drones_num_on_van)]
        self.dockhubs_constrains: list[DockingHub_Constrains] = [DockingHub_Constrains(self.grb_var.route.nodes_docking_hubs[i])
                                                                 for i in range(dockhub_num)]
        self.depot_constrain: Depot_Constrains = Depot_Constrains()

    # def initial_solution(self):

    def objective_fn(self):
        """
        the weight_van*solution_van + weight_dro*solution_dro[0] + weight_dro*solution_dro[1] + fixed_cost
        :return: the current best objective
        """
        from Classes.PARAMs import fixed_cost
        for n in range(drones_num_on_van):
            for i in self.grb_var.nodes_oder:
                for j in self.grb_var.nodes_oder:
                    temp = self.var_dro[0][i, j]*self.dict_dro[i, j] + self.var_dro[0][i, j]*self.dict_dro[i, j]\
                         + self.var_van[i, j]*self.dict_van[i, j]
                    self.obj += temp

        self.obj += fixed_cost

        if self.bst_obj<=self.obj:
            return self.bst_obj
        elif self.bst_obj>=self.obj:
            # update the best objective result and the related solution
            self.bst_obj = self.obj
            self.bst_sol.update({'van': self.var_van, 'dros': self.var_dro})
            return self.bst_obj

    def initial_solution(self):
        """
        generate the initial solution randomly
        :return:
        """
        from random import choice
        # print("======> before ", self.var_van)
        [self.var_van.update({i: choice([0,1])}) for i in list(self.var_van.keys())]
        # print("======> after ", self.var_van)
        [self.var_dro[n].update({i: choice([0,1])}) for n in range(drones_num_on_van) for i in list(self.var_dro[n].keys())]
        self.vars = {'van': self.var_van, 'dros': self.var_dro}

        self.sa_model.set_current_state(self.vars)

    def evaluate_constrs(self):
        flag: bool = False
        # ------------ Customer Demand Constrains ----------------------------------------------------------------------

        # ------------ Energy Constrains -------------------------------------------------------------------------------
        # ------------

        # ------------ Non Flying Zone Constrains ----------------------------------------------------------------------

        # ------------ Packages Reload ---------------------------------------------------------------------------------

        return flag

    def invalid_Sol(self):
        return "invalid solution"

    def mutate_solution(self):
        """
        Exchange the connectivity of some routes of the drones and van matrixes
        :return: the new solution that has mutated
        """
        list_van_1: list = list(self.var_van.keys())
        list_van_2: list = np.random.permutation(list_van_1)
        list_van_3: list = np.random.permutation(list_van_2)
        list_dro0_1: list = list(self.var_dro[0].keys())
        list_dro0_2: list = np.random.permutation(list_dro0_1)
        list_dro0_3: list = np.random.permutation(list_dro0_2)
        list_dro1_1: list = list(self.var_dro[1].keys())
        list_dro1_2: list = np.random.permutation(list_dro1_1)
        list_dro1_3: list = np.random.permutation(list_dro1_2)
        for i in range(len(list_van_2)):
            self.var_van.update(np.random.choice([{i:self.vars['van'][list_van_1[i]]},
                                                 {i:self.vars['van'][list_van_2[i]]},
                                                 {i:self.vars['van'][list_van_3[i]]},]))
            self.var_dro[0].update(np.random.choice([{i:self.vars['van'][list_dro0_1[i]]},
                                                     {i:self.vars['van'][list_dro0_2[i]]},
                                                     {i:self.vars['van'][list_dro0_3[i]]},]))
            self.var_dro[1].update(np.random.choice([{i:self.vars['van'][list_dro1_1[i]]},
                                                     {i:self.vars['van'][list_dro1_2[i]]},
                                                     {i:self.vars['van'][list_dro1_3[i]]},]))
        self.vars = {'van': self.var_van, 'dros': self.var_dro}
        return self.vars

    def other_new_generation(self):
        index = list(self.var_van.keys())
        for i in range(len(self.var_van)):
            temp = 0
            a = np.random.choice(set(range(len(self.var_van)))-set(i))
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

    def new_solution(self, i: int):
        fun = self.sol_dict.get(i, self.invalid_Sol)
        return fun()


sa_controller = SA_Controller()
sa_controller.initial_solution()