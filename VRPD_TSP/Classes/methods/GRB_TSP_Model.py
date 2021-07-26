#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.methods.GRB_Var_Constrs import GRB_Var_Constrs
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from Classes.PARAMs import rate_load_pack_drone, rate_load_pack_van

class GRB_TSP_Model:
    def __init__(self):
        self.m: gp.Model = gp.Model()
        self.grb_var: GRB_Var_Constrs = GRB_Var_Constrs()

        # ------------ Raw Data ----------------------------------------------------------------------------------------
        self.graph_data: list = list(self.grb_var.graph.edges.data("weight"))
        self.dict_weight: dict = {(i,j): distance for i,j,distance in self.graph_data}
        self.dict_dro_0: dict = {(i,j): distance*rate_load_pack_drone for i,j,distance in self.graph_data}
        self.dict_dro_1: dict = {(i,j): distance*rate_load_pack_van for i,j,distance in self.graph_data}
        self.dict_van: dict = {(i,j): distance*rate_load_pack_van for i,j,distance in self.graph_data}

        # ------------ Gurobi: Variables -------------------------------------------------------------------------------
        self.vars: dict = dict()
        self.add_variable()

        # ------------ Gurobi: Constrains ------------------------------------------------------------------------------
        self.add_constrains()
        # ------------ Gurobi: Optimization ----------------------------------------------------------------------------
        self.model_optimization()

    def add_variable(self):
        var_dro_0: gp.Var = self.m.addVars(self.dict_dro_0.keys(), obj=self.dict_dro_0, vtype=GRB.BINARY, name='var_dro_0')
        self.m.update()
        # print('------- 1 ', self.m.getVars(), '\n', len(self.m.getVars()))
        var_dro_1: gp.Var = self.m.addVars(self.dict_dro_1.keys(), obj=self.dict_dro_1, vtype=GRB.BINARY, name='var_dro_1')
        self.m.update()
        # print('------- 2 ', self.m.getVars(), '\n', len(self.m.getVars()))
        var_van: gp.Var = self.m.addVars(self.dict_van.keys(), obj=self.dict_van, vtype=GRB.BINARY, name='var_van')
        self.m.update()
        # print('------- 3 ', self.m.getVars(), '\n', len(self.m.getVars()))
        self.vars.update({'dro_0':var_dro_0})
        self.vars.update({'dro_1':var_dro_1})
        self.vars.update({'van':var_van})

    def add_constrains(self):
        # ------------ Energy Constrains for van and drones ------------------------------------------------------------
        from Classes.PARAMs import max_range_van, flying_range_drone
        self.m.addConstr(self.vars['van'].sum()<=max_range_van, name='energy_van')
        self.m.addConstr(self.vars['dro_0'].sum()<=flying_range_drone, name='energy_dro_0')
        self.m.addConstr(self.vars['dro_1'].sum()<=flying_range_drone, name='energy_dro_1')
        # ------------ Customer Demand for van and drones --------------------------------------------------------------
        self.m.addConstrs((gp.quicksum([self.vars['van'].sum(i, '*'),
                                        self.vars['dro_0'].sum(i, '*'),
                                        self.vars['dro_1'].sum(i, '*')]) <= self.grb_var.customer_demand[i]
                           for i in self.grb_var.nodes_oder), name='cus_demand')
        # This expression equals to the following:
        # for i in self.grb_var.nodes_oder:
        #     a = gp.quicksum([self.vars['van'].sum(i, '*'),
        #                      self.vars['dro_0'].sum(i, '*'),
        #                      self.vars['dro_1'].sum(i, '*')])
        #     self.m.addConstr((a <= self.grb_var.customer_demand[i]), name='cus_demand')

        # ------------ Non Fly Range for the drones --------------------------------------------------------------------
        # print(self.grb_var.non_fly_zone[self.grb_var.nodes_oder[0]])
        self.m.addConstrs((gp.quicksum([self.vars['dro_0'].sum(i, '*'),
                                        self.vars['dro_1'].sum(i, '*')]) <= 0
                           for i in self.grb_var.nodes_oder
                           if self.grb_var.non_fly_zone[i] == 1), name='non_fly')

    def model_optimization(self):
        self.m.ModelSense = GRB.MINIMIZE
        self.m.Params.lazyConstraints = 1
        self.m.setParam(GRB.Param.PoolSolutions, 100)
        self.m.optimize()

        # self.m._vars.update(self.vars['dro_0'][i])

temp = GRB_TSP_Model()
