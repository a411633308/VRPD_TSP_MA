#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
from Classes.Packages import Packages
from Classes.Batteries import Batteries
# from Classes.Docking_hubs import Docking_hubs
import random
import math
from Classes.PARAMs import flying_range_drone, max_range_van, max_pack_num_van, max_bat_num_van
from Classes.PARAMs import rate_load_range_van, rate_load_pack_van
class Minivan:
    def __init__(self, max_range: int = max_range_van, max_pack: int = max_pack_num_van,
                 fly_range: int = flying_range_drone, num: int = max_bat_num_van):
        """
        a minivan which can load several drones, deliver packages, change drone's batteries, etc.
        :param max_range: the maximum running range of the van
        :param max_pack: the maximum number of packages can be saved on the van
        :param fly_range: the maximum flying range of the drone
        :param num: the numbers of battery can be saved on the van
        """
        self.index: str = "van_" + str(uuid.uuid1())[:10]
        self.packages: list = list()
        # packages: receive reservation, reserve; unload to drone;
        #           load from docking_hubs
        self.rec_pack_res_num: int = 0
        self.res_pack_list: list = list()
        self.left_pack: int = len(self.packages)
        self.del_cus_list: list = list()
        self.max_packages_num: int = max_pack

        # energy: fuel state
        self.max_range: int = max_range
        self.left_fuel: int = self.max_range

        # energy: batteries
        self.rec_bat_res_num: int = 0
        self.batteries: list = list()
        self.max_bat_num: int = 0
        self.left_bat_num: int = len(self.batteries)
        self.ini_batteries(flying_range=fly_range, num=num)
        self.rate_load_range_van: float = rate_load_range_van
        self.rate_load_pack_van: float = rate_load_pack_van

    def __index__(self):
        return self.index

    def __eq__(self, other):
        return self.index == other.index

    def __str__(self):
        return "+" * 12 + self.index + " minivan has left fuel " + str(self.left_fuel) + "+" * 12

    # >--------------------functions for packages--------------------start
    def receive_pack_reservation(self):
        """
        increases when the minivan receives a package reservation
        :return: package reservation orders
        """
        self.rec_pack_res_num += 1
        return self.rec_pack_res_num

    def get_receive_pack_reservation(self):
        """
        return packages reservation received from drones
        :return: number of packages reservation received
        """
        return self.rec_pack_res_num

    def load_packages(self):
        """
        load a certain numbers of packages to the minivan
        :return: 1
        """
        num = self.left_fuel * self.rate_load_range_van
        [self.packages.append(Packages()) for i in range(num)]
        self.left_pack: int = len(self.packages)
        self.left_fuel = self.left_fuel*math.pow((1-self.rate_load_pack_van), self.left_pack)
        return 1

    def unload_to_drone(self, node: list):
        """
        unload required packages to the drone
        :param node:  given list of customer needs
        :return: 1
        """
        pack_index = [i for i in range(len(self.packages)) for j in range(len(node))
                      if self.packages[i].index == node[j]]
        print("found packages indexes are: ", pack_index)
        print("+"*12 + " Left packages and packages reservation " + "before unloading " + str(self.left_pack) + " " + str(self.rec_pack_res_num) + " " + "+"*12)
        [self.packages.pop(pack_index[i]) for i in range(len(pack_index))]

        self.rec_pack_res_num = self.rec_pack_res_num - len(pack_index)
        self.left_pack = len(self.packages)
        self.left_fuel = self.left_fuel * math.power((1-self.left_fuel), len(pack_index))
        # unloading packages increases the distance the van can still run
        print("+"*12 + " Left packages and packages reservation " + "after unloading " + str(self.left_pack) + " " + str(self.rec_pack_res_num) + " " + "+"*12)
        return 1

    def deliver(self, w: float):
        """the van deliver packages through the needs but not the index of packages"""
        self.del_cus_list.append(self.packages[0])
        self.packages.pop(0)
        self.left_fuel = (self.left_fuel - w)*(1+self.rate_load_range)
        self.left_pack = len(self.packages)
        return 1

    def deliver(self, cus_needs: str, w: float):
        """
        deliver the packages to the customers
        :param cus_needs: the customer needs, namely the index of required package
        :param w: the minivan's cost to get the customer's location
        :return:1
        """
        pack_index = [i for i in range(len(self.packages)) if self.packages[i].index == cus_needs]
        print(pack_index)
        self.packages.pop(pack_index[0])
        self.left_fuel = (self.left_fuel - w)*(1+self.rate_load_range)
        self.left_pack = len(self.packages)
        self.del_cus_list.append(cus_needs)
        print("+" * 12 + " delivers a package successfully. " + "+" * 12)
        return 1

    def reserve(self, node: str):
        """
        when the left packages are empty on the minivan, reserves from docking hubs
        :param node: str, the index of docking hubs that has received the package reservation
        :return: 1
        """
        self.res_pack_list.append(node)
        return 1

    # <--------------------functions for packages--------------------end

    # >--------------------functions for batteries--------------------start
    def receive_bat_reservation(self):
        """
        get battery reservation from a drone
        :return: 1
        """
        self.rec_bat_res_num += 1
        return 1

    def get_bat_reservation(self):
        return self.rec_bat_res_num

    def ini_batteries(self, num: int, flying_range: int):
        """
        initiate the batteries saved in the minivan for drones
        :param num: number of batteries for drones
        :param flying_range: maximum flying range of drones
        :return: list of batteries initiated
        """
        [self.batteries.append(Batteries(flying_range)) for i in range(num)]
        self.left_bat_num = len(self.batteries)
        self.max_packages_num = len(self.batteries)
        return 1

    def get_batteries(self):
        return self.batteries

    def change_batteries(self):
        """
        changes the first battery to the drone
        :return: 1
        """
        batter = self.batteries[0]
        self.batteries.pop(0)
        self.left_bat_num -= 1
        return batter
    # <--------------------functions for batteries--------------------end


# max_range = 825
# max_pack = 56
# fly_range = 352
#
# minivan_1 = Minivan(max_range, max_pack)
# [minivan_1.receive_pack_reservation() for i in range(8)]
# print(minivan_1.get_receive_pack_reservation())
# minivan_1.load_packages()
# print(minivan_1.packages[0].index)
# minivan_1.deliver(minivan_1.packages[0].index, 26)
# print(minivan_1.del_cus_list)
# a = [minivan_1.packages[i].index for i in range(1,5)]
# print(a)
# minivan_1.unload_to_drone(a)
#
# dck_hubs = Docking_hubs(6,fly_range)
# minivan_1.reserve(dck_hubs.index)
# [minivan_1.receive_bat_reservation() for i in range(5)]
# print(minivan_1.get_bat_reservation())
# minivan_1.ini_batteries(13, fly_range)
# print(len(minivan_1.get_batteries()))
# print(" Baatteries changed", minivan_1.change_batteries())
