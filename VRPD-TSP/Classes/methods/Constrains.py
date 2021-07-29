#!/usr/bin/python
# -*- coding: UTF-8 -*-

# import numpy as np
# import random
# from Classes.methods.Solution import Solution

class Constrains:
    def __init__(self, max: int):
        """
        saves no data, but judges firstly then recall the relevant function in classes.
        :param max: maximum capacity of the resource.
        """
        self.max: int = max
        self.weight: list = list() # resources consumed or used
        self.left: any = self.max

    def change(self, weight: int):
        """
        If the left resource satisfies the required, then do the change.
        :param weight: int,
        once resources requirements
        :return: int,
        changed successfully, left resources; unsuccessfully, 0.
        """
        if weight <= self.left:
            self.weight.append(weight)
            self.left -= self.weight[-1]
            return self.left
        else:
            return 0

    def reset(self):
        self.left = self.max

#cons = Constrains(234)

# route_params: list = [2, 200, [random.choice(range(0, 1)), False]]
# non_fly_num: int = 1
# graph_params: list = [2, 3, 26]
# # the color of customer, depot and docking hub nodes: skyblue, red, and orange
# initial_solution = Solution(route_params=route_params, graph_params=graph_params, seed_num=1200,
#                             non_fly_num=non_fly_num, color_list=['skyblue', 'red', 'orange'])
# # initial_solution.plot_graph()  # plot the complete graph
# # ---initiate the related parameters to generate solution matrices
# initial_solution.weights_adj_matrix()
# # ------generate matrix randomly
# initial_solution.generate_solution_matrix_randomly(2)
# # ------whether the solution satisfy the requirements
