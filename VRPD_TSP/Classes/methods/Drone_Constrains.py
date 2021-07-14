#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.Drones import Drones
from Classes.Batteries import Batteries
from Classes.Packages import Packages
from Classes.methods.Constrains import Constrains
import random

class Drone_Batteries(Constrains):
    def __init__(self, drone: Drones):
        self.battery: Batteries = drone.battery
        self.max: float = self.battery.flying_range
        self.left: float = self.battery.left_ba_sta
        self.weight: float = 0.0  # the used energy of battery of the drone
        self.reserve: list[str] = list()

    def use(self, w: float):
        if self.left > w:
            self.weight += w
            self.left -= w
            return 1
        else:
            return 0

    def change(self, battery: Batteries):
        self.battery = battery
        self.left = self.battery.left_ba_sta

    def reserve_battery(self, node: str, clst_node_cost: float):
        """
        the minimum cost for the drone to get the closet minivan or docking hub nodes.
        :param node: the index of node who will receive the battery reservation of the drone
        :param clst_node_cost:
        :return: successfully, 1; unsuccessfully, 0.
        """
        if self.battery.left_ba_sta >= clst_node_cost:
            self.reserve.append(node)
            return 1
        else:
            return 0


class Drone_Packages(Constrains):
    def __init__(self, drone: Drones):
        """
        Constrains for the drone to manage the packages on the drone
        :param drone: the relevant drone
        """
        self.drone: Drones = drone
        self.packages: list[Packages] = drone.package
        self.max: int = len(self.packages)  # the maximum number of packages that can be saved on the drone
        self.left: int = self.max  # the left packages on the drone
        self.weight: list[Packages] = list()
        self.reserve_list: list[str] = list()

    def deliver(self, required_pack: str):
        pack_index = [i for i in range(len(self.packages)) if self.packages[i].index == required_pack]
        if len(pack_index) != 0:
            self.weight.append(self.packages[pack_index[0]])
            self.packages.pop(pack_index[0])
            self.left = len(self.packages)
            return 1
        else:
            return 0

    def reserve_package(self, node: str):
        if self.left <= 1:
            self.reserve_list.append(node)

    def load_packages(self, num: int):
        if self.left <= 1:
            self.drone.load_packages(num)
            self.left = len(self.drone.left_packages)
            self.packages = self.drone.package
            return 1
        else:
            return 0

class Drone_Constrains:
    def __init__(self, drone: Drones):
        self.drones: Drones = drone
        self.drone_packages: Drone_Packages = Drone_Packages(self.drones)
        self.drone_batteries: Drone_Batteries = Drone_Batteries(self.drones)

    def deliver_package(self, cust_needs: str, w: float):
        """
        the function that manages the deliver action of the drone
        :param cust_needs: the index of packages that is required by a customer
        :return: successfully, 1; unsuccessfully, 0
        """
        flag_1 = self.drone_batteries.use(w)
        flag_2 = self.drone_packages.deliver(cust_needs)
        if flag_1 == 1 and flag_2 == 1:
            return 1
        else:
            return 0

    def reserve_packages(self, node: str, clst_node: float, clst_cust: float):
        """
        If the left battery on the drone is still enough to get at least one package and deliver
        :param node: the index of the closet node, who receives the drone's package reservation
        :param clst_node: float,
        the costs of the drone to the closet minivan or docking hub node
        :param clst_cust: float,
        the costs of the drone to the closet customer node
        :return: successfully, 1; unsuccessfully, 0.
        """
        if self.drone_batteries.left >= 2 * clst_node + 2 * clst_cust:
            self.drone_packages.append(node)
            return 1
        else:
            return 0

    def load_packages(self, rate=random.uniform(0.1, 0.5)):
        num = self.drone_batteries * rate
        self.drone_packages.load_packages(num)
        self.drone_batteries.left = self.drones.battery.left_ba_sta

    def change_battery(self, node_has_battery: bool, closet_customer: float, battery_node: Batteries):
        """
        when the drone is currently at a docking hub of minivan, can choose change battery or not
        :param battery_node: the given battery from a docking hub or a minivan
        :param node_has_battery: whether the current node contains a full-charged battery or not
        :param closet_customer: the left battery of the drone to the closet customer node
        :return: successfully, 1; unsuccessfully, 0.
        """
        if node_has_battery > 1 & self.drone_batteries.left <= 2 * closet_customer:
            self.drone_batteries.change(battery_node)
            return 1
        else:
            return 0

    def stop_drone(self, node_has_no_battery: bool, closet_customer: float):
        if not node_has_no_battery & self.drone_batteries <= closet_customer * 2:
            return self.drones
        else:
            return 0
