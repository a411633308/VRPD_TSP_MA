#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.methods.GRB_Var_Constrs import GRB_Var_Constrs
import math
from itertools import combinations, product
from Classes.PARAMs import drones_num_on_van
import gurobipy as gp
from gurobipy import GRB

class GRB_Models:
    def __init__(self):
        self.GRB_var: GRB_Var_Constrs = GRB_Var_Constrs()
        self.model: gp.Model = gp.Model()
        self.var_van: gp.Var = self.model.addVar(vtype=GRB.BINARY, name='van_solution')
        self.var_drones: list[gp.Var] = [self.model.addVar(self.GRB_var.solution_matrix_drones[i])
                                         for i in range(drones_num_on_van)]
        print(type(self.var_van))

grb_model = GRB_Models()
