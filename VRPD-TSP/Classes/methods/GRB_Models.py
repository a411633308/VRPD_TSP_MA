#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.methods.GRB_Var_Constrs import GRB_Var_Constrs
import math
from itertools import chain
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from Classes.PARAMs import drones_num_on_van


class GRB_Models:
    def __init__(self):
        self.GRB_var: GRB_Var_Constrs = GRB_Var_Constrs()
        self.model: gp.Model = gp.Model()

        # ------------ Variables for the Gurobi models -----------------------------------------------------------------
        self.var_van: gp.Var = self.model.addMVar(shape=(self.GRB_var.nodes_len, self.GRB_var.nodes_len),
                                                  vtype=GRB.BINARY, name='van_solution')
        self.var_drones: list[gp.Var] = [self.model.addMVar(shape=(self.GRB_var.nodes_len, self.GRB_var.nodes_len),
                                                            vtype=GRB.BINARY, name='drones_solution' + str(i))
                                         for i in range(drones_num_on_van)]

        # self.vars_example = self.model.addVars(self.GRB_var.nodes_oder, vtype = GRB . BINARY , name ='e')
        # print(type(self.vars_example))

        # ------------ Constrains for the Gurobi models ----------------------------------------------------------------
        # ------------ 1. customer demand ------------------------------------------------------------------------------
        self.demand_constrs_dro: list[gp.Var] = [self.model.addConstrs((
            self.var_drones[j][i].sum() <= self.GRB_var.customer_demand[self.GRB_var.nodes_oder[i]]
            for i in range(self.GRB_var.nodes_len)), 'demand_constrs_dro_' + str(j))
            for j in range(drones_num_on_van)]
        self.demand_constrs_van: gp.Constr = self.model.addConstrs((
            self.var_van[i].sum() <= self.GRB_var.customer_demand[self.GRB_var.nodes_oder[i]]
            for i in range(self.GRB_var.nodes_len)), 'deman_constrs_van')

        # ------------ 2. non fly zone ---------------------------------------------------------------------------------
        self.non_fly_constrs: list[gp.Constr] = self.non_fly_constrs_fn()

        # ------------ 3. connection -----------------------------------------------------------------------------------
        self.connection_constr_dro: list[gp.Constr] = [self.model.addConstrs((
                         self.var_drones[n][i].sum() <= self.GRB_var.adj_matrix[i].sum()
                         for i in range(self.GRB_var.nodes_len)), "connection_constrs_dro_{i}")
                                                       for n in range(drones_num_on_van)]
        # solution matrix of the drones should cover no routes who are not connected in the adjacency matrix of the overall graph.
        self.connection_constr_van: gp.Constr = self.model.addConstrs((
                         self.var_van[i].sum() <= self.GRB_var.adj_matrix[i].sum()
                         for i in range(self.GRB_var.nodes_len)), 'connection_constr_van')
        # solution matrix of the van should be as upper condition as well.
        print(self.GRB_var.adj_matrix[1].sum())
        self.connection_constr: gp.Constr = self.model.addConstr((
            gp.quicksum([self.var_van[i], self.var_drones[0][i], self.var_drones[1][i]])
            >= self.GRB_var.adj_matrix[i].sum()
            for i in range(self.GRB_var.nodes_len)),'connection_constr')

        # ------------ Optimize the model ------------------------------------------------------------------------------
        self.optimize_model()

    def non_fly_constrs_fn(self):
        non_fly_constrs: list[gp.Constr] = list()
        for n in range(drones_num_on_van):
            for i in range(self.GRB_var.nodes_len):
               if (sum(self.GRB_var.non_fly_zone[i]) == 1).all():
                  non_fly_constrs.append(self.model.addConstr((self.var_drones[n][i].sum() <= 0),
                                                                   'non_fly_constrs_' + str(n)))
        return non_fly_constrs

    def optimize_model(self):
        import random
        from Classes.PARAMs import seed_num
        import numpy as np
        random.seed(seed_num)
        fixed_cost: int = random.randint(200,300)
        a = self.GRB_var.weight_matrix*self.GRB_var.van_rate_load_matrix
        b = self.GRB_var.weight_matrix*self.GRB_var.dro_rate_load_matrix

        self.model.ModelSense = GRB.MINIMIZE
        self.model.setObjectiveN(self.var_van.sum(), index=1)
        [self.model.setObjectiveN(self.var_drones[i].sum(), index=i+2) for i in range(drones_num_on_van)]

        # self.model.write('./../../Results/Models/Model_demo.lp')
        self.model.optimize()
        print(self.model.getObjective())



grb_model = GRB_Models()
