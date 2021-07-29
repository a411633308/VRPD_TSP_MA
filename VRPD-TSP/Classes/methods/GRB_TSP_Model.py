#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.methods.GRB_Var_Constrs import GRB_Var_Constrs
import numpy as np
import gurobipy as gp
from gurobipy import GRB
from Classes.PARAMs import rate_load_pack_drone, rate_load_pack_van
from Classes.methods.SA_Model import SA_Model

class GRB_TSP_Model:
    def __init__(self):
        self.m: gp.Model = gp.Model()
        self.grb_var: GRB_Var_Constrs = GRB_Var_Constrs()

        # ------------ Raw Data ----------------------------------------------------------------------------------------
        self.graph_data: list = list(self.grb_var.graph.edges.data("weight"))
        self.dict_weight: dict = {(i,j): distance for i,j,distance in self.graph_data}
        self.dict_dro_0: dict = {(i+'dro_0',j+'dro_0'): distance*rate_load_pack_drone for i,j,distance in self.graph_data}
        self.dict_dro_1: dict = {(i+'dro_1',j+'dro_1'): distance*rate_load_pack_van for i,j,distance in self.graph_data}
        self.dict_van: dict = {(i+'van',j+'van'): distance*rate_load_pack_van for i,j,distance in self.graph_data}
        # ------------ Gurobi: Variables -------------------------------------------------------------------------------
        self.vars: dict = dict()
        self.add_variable()
        self.m._logfile = open('./../../Results/logs/log_file.cb', 'w')
        # ------------ Simulated Annealing Algorithm -------------------------------------------------------------------
        self.sa_model: SA_Model = SA_Model(self.m._vars)

        # ------------ Gurobi: Constrains ------------------------------------------------------------------------------
        self.add_constrains()
        # ------------ Gurobi: Optimization ----------------------------------------------------------------------------
        self.model_optimization()

    def add_variable(self):

        # object in solution matrix: 1, covered by van; 2, covered by drone_0; 3, covered by drone_1
        #                            4, covered by van with one drone; 5, covered by van with two drones
        var_dro_0 = self.m.addVars(self.dict_dro_0.keys(), obj=self.dict_dro_0, vtype=GRB.BINARY, name='var_dro_0')
        self.m.update()
        # print('------- 1 ', self.m.getVars(), '\n', len(self.m.getVars()))
        var_dro_1 = self.m.addVars(self.dict_dro_1.keys(), obj=self.dict_dro_1, vtype=GRB.BINARY, name='var_dro_1')
        self.m.update()
        # print('------- 2 ', self.m.getVars(), '\n', len(self.m.getVars()))
        var_van = self.m.addVars(self.dict_van.keys(), obj=self.dict_van, vtype=GRB.BINARY, name='var_van')
        self.m.update()
        # print('------- 3 ', self.m.getVars(), '\n', len(self.m.getVars()))

        self.m._vars = var_van
        # for a, b in var_van:
        #     print(a, b, var_van[a, b])
        # print("________1 ", len(self.m._vars))
        [self.m._vars.update({(i, j): var_dro_0[i, j]}) for i, j in var_dro_0]
        # print("________2 ", len(self.m._vars))
        [self.m._vars.update({(i, j): var_dro_1[i, j]}) for i, j in var_dro_1]
        # print("________3 ", len(self.m._vars))
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
        # ------------- Drones must take off with van at Depot ---------------------------------------------------------
        for i in list(self.dict_van.keys()):
            if i[0][:3] == 'dep' and i[1][:3] != 'cus':
                self.m.addConstr(self.vars['van'][i] == self.dict_van[i], name='van_depot')

        for i in list(self.dict_dro_0.keys()):
            if i[0][:3] == 'dep' and i[1][:3] != 'cus':
                self.m.addConstr(self.vars['dro_0'][i] == 0, name='dro_depot')

        for i in list(self.dict_dro_1.keys()):
            if i[0][:3] == 'dep' and i[1][:3] != 'cus':
                self.m.addConstr(self.vars['dro_1'][i] == 0, name='dro_depot')

        # if the route is not from a depot to a customer node, it must be covered by van but not drones.
        # keys = list(self.dict_van.keys())
        # print("------------------------ ",self.vars['van'][keys[0]], '\n', keys[0][0])


        # ------------ Customer Demand for van and drones --------------------------------------------------------------
        a = self.m.addConstrs((gp.quicksum([self.vars['van'].sum(i+'van', '*'),
                                        self.vars['dro_0'].sum(i+'dro_0', '*'),
                                        self.vars['dro_1'].sum(i+'dro_1', '*')]) <= self.grb_var.customer_demand[i]
                           for i in self.grb_var.nodes_oder), name='cus_demand')
        print("*********** the constrain of dro_1 is: ", a, '\n', type(a))
        # This expression equals to the following:
        # for i in self.grb_var.nodes_oder:
        #     a = gp.quicksum([self.vars['van'].sum(i, '*'),
        #                      self.vars['dro_0'].sum(i, '*'),
        #                      self.vars['dro_1'].sum(i, '*')])
        #     self.m.addConstr((a <= self.grb_var.customer_demand[i]), name='cus_demand')

        # ------------ Non Fly Range for the drones --------------------------------------------------------------------
        # print(self.grb_var.non_fly_zone[self.grb_var.nodes_oder[0]])
        self.m.addConstrs((gp.quicksum([self.vars['dro_0'].sum(i+'dro_0', '*'),
                                        self.vars['dro_1'].sum(i+'dro_1', '*')]) <= 0
                           for i in self.grb_var.nodes_oder
                           if self.grb_var.non_fly_zone[i] == 1), name='non_fly')

    def model_optimization(self):
        self.m.ModelSense = GRB.MINIMIZE
        # self.m.Params.lazyConstraints = 1
        # self.m.setParam(GRB.Param.PoolSolutions, 100)
        # self.m.optimize(self.SA_callback)

    def SA_callback(self, model, where):
        if where == GRB.Callback.POLLING:
            # ignore polling callback
            pass

        elif where == GRB.Callback.MIPSOL:
            # MIP solution callback
            nodecnt = model.cbGet(GRB.Callback.MIPSOL_NODCNT)
            obj = model.cbGet(GRB.Callback.MIPSOL_OBJ)
            solcnt = model.cbGet(GRB.Callback.MIPSOL_SOLCNT)
            x = model.cbGetSolution(model._vars)
            print('**** New solution at node %d, obj %g, sol %d, x[0] = %g ****' % (nodecnt, obj, solcnt, x))

        elif where == GRB.Callback.MESSAGE:
            # Message callback
            msg = model.cbGet(GRB.Callback.MSG_STRING)
            model._logfile.write(msg)

        elif where == GRB.Callback.MIPNODE:
            # MIP node callback
            if self.sa_model.current_temp>self.sa_model.final_temp:
                print('******** Current temperature is ', self.sa_model.current_temp, ' < ', self.sa_model.final_temp, ' ********')
                self.sa_model.change_current_temp()
                if model.cbGet(GRB.Callback.MIPNODE_STATUS) == GRB.Status.OPTIMAL:
                    x = model.cbGetNodeRel(model._vars)
                    model.cbSetSolution(model.getVars(), x)

temp = GRB_TSP_Model()

def SA_callback(model, where):
    if where == GRB.Callback.POLLING:
        # ignore polling callback
        pass

    # elif where == GRB.Callback.MIPSOL:
    #     # MIP solution callback
    #     nodecnt = model.cbGet(GRB.Callback.MIPSOL_NODCNT)
    #     obj = model.cbGet(GRB.Callback.MIPSOL_OBJ)
    #     solcnt = model.cbGet(GRB.Callback.MIPSOL_SOLCNT)
    #     x = model.cbGetSolution(model._vars)
    #     print('**** New solution at node %d, obj %g, sol %d, x[0] = %g ****' % (nodecnt, obj, solcnt, x))

    elif where == GRB.Callback.MESSAGE:
        # Message callback
        msg = model.cbGet(GRB.Callback.MSG_STRING)
        model._logfile.write(msg)

    elif where == GRB.Callback.MIPNODE:
        # MIP node callback
        if temp.sa_model.current_temp>temp.sa_model.final_temp:
            print('******** Current temperature is ', temp.sa_model.current_temp, ' < ', temp.sa_model.final_temp, ' ********')
            temp.sa_model.change_current_temp()
            if model.cbGet(GRB.Callback.MIPNODE_STATUS) == GRB.Status.OPTIMAL:
                x = model.cbGetNodeRel(model._vars)
                model.cbSetSolution(model.getVars(), x)


temp.m.optimize(SA_callback)
