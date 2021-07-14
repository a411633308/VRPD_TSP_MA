#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.Packages import Packages
from Classes.Batteries import Batteries
from Classes.Minivan import Minivan

from random import choice

class Resources:
    def __init__(self):
        self.batteries_list: list[Batteries] = list()
        self.batteries_num: int = len(self.batteries_list)
        self.packages_list: list[Packages] = list()
        self.packages_num: int = len(self.packages_list)

    def collect_overall_resources(self,minivan: Minivan, drones: list, dck_hubs: list):
        # collect batteries in overall network
        #           batteries in minivan
        [self.batteries_list.append(minivan.batteries[i]) for i in range(len(minivan.batteries))]
        #           batteries in drones
        [self.batteries_list.append(drones[i].battery) for i in range(len(drones))]
        #           batteries in docking hubs
        [self.batteries_list.append(dck_hubs[i].batteries[j]) for i in range(len(dck_hubs))
         for j in range(len(dck_hubs[i].batteries))]
        self.batteries_num = len(self.batteries_list)

        # collect packages in overall network
        #           packages in minivan
        [self.packages_list.append(minivan.packages[i]) for i in range(len(minivan.packages))]
        #           packages in drones
        [self.packages_list.append(drones[i].package[j]) for i in range(len(drones)) for j in range(len(drones[i].package))]
        #           packages in docking hubs
        [self.packages_list.append(dck_hubs[i].packages[j]) for i in range(len(dck_hubs))
         for j in range(len(dck_hubs[i].packages))]
        self.packages_num = len(self.packages_list)
        print("given batteries and packages in the network: ", self.batteries_num, self.packages_num)

    def get_batteries_overall(self):
        return self.batteries_list

    def get_packages_overall(self):
        return self.packages_list

    def get_a_package(self):
        chosen = choice(self.packages_list)
        print("Chosen package: ", chosen)
        return [chosen]

    def get_a_package(self, pck_num: int):
        chosen = [choice(self.packages_list) for i in range(pck_num)]
        print("Chosen packages number: ", len(chosen))
        return chosen

