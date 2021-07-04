#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
from Classes.Packages import Packages
from Classes.Batteries import Batteries
# from Classes.Docking_hubs import Docking_hubs

class Drones:
    def __init__(self, flying_range: int):
        """
        The drone node.
        :param flying_range: maximum flying range of the drone
        """
        self.index: str = "dro_"+str(uuid.uuid1())[:10]
        # about battery
        self.flying_range: int = flying_range  # think twice which kind of type should be used
        self.battery: Batteries = Batteries(self.flying_range)
        self.energy_consumption: int = 0  # sum of Wro_dr i, i = N+
        self.bat_res_list: list = list()

        # about packages
        self.package: list = list()
        self.left_packages: int = len(self.package)
        self.package_delivered: list = list()
        self.pack_res_list: list = list()

    def __index__(self):
        return self.index

    def __eq__(self, other):
        return self.index == other.index

    def __str__(self):
        return "The drone " + self.index + "has " + str(len(self.package)) + \
            " packages in warehouses, " + "left energy " + \
            str(self.battery.left_ba_sta) + ", and packages delivered " + \
            str(self.package_delivered)

    # >--------------------functions for packages--------------------start
    def load_packages(self, num: int):
        """
        This drone loads packages from a minivan/docking hub
        :param num: packages loaded once
        :return: 1
        """
        [self.package.append(Packages()) for i in range(num)]
        self.left_packages: int = len(self.package)
        print("+"*12 + " load " + str(num) + " packages to the drone " + self.index + " " + "+"*12)
        return 1

    def deliver(self, cu_needs: str, w: int):
        print("+"*12 + " Left packages before delivery:" + str(self.left_packages) + " " + "+"*12)
        pack_index = [i for i in range(len(self.package)) if self.package[i].index == cu_needs]
        self.package_delivered.append(cu_needs)
        self.package.pop(pack_index[0])
        self.left_packages: int = len(self.package)
        print("+"*12 + " Left packages after delivery:" + str(self.left_packages) + " " + "+"*12)
        self. sum_energy_consumption(w)
        return 1

    def get_left_packages(self):
        return self.package

    def get_left_packages_num(self):
        self.left_packages: int = len(self.package)
        return self.left_packages

    def reserve(self, nodes: str):
        """
        #Drone/Minivan# reserves packages
        :param nodes: the index who receives the packages reservation.
        :return: 1
        """
        self.pack_res_list.append(nodes)
        return 1

    def get_pack_reservation(self):
        """
        get the list of packages reservation received from #drones/minivans#
        :return: packages reservation received
        """
        return self.pack_res_list

    # <--------------------functions for packages--------------------end

    # >--------------------functions for energy--------------------start
    def battery_changed(self):
        """
        Batteries is being changed, its reservation empties too.
        :return:1
        """
        self.battery: Batteries = Batteries(self.flying_range)
        self.battery.ba_res_list = list()
        return 1

    def sum_energy_consumption(self, w: int):
        """
        Total energy consumptions adds, and battery states decreases.
        :param w:
        :return:1
        """
        self.energy_consumption += w
        self.battery.use_battery(w)
        return 1

    def reserve_battery(self, node: str):
        """
        This drone reserves a battery from a docking hub/minivan
        :param node: the index of the docking hub/minivan
        :return: 1
        """
        self.bat_res_list.append(node)
        return 1

    def get_bat_reservation(self):
        return self.bat_res_list

    # <--------------------functions for energy--------------------end

#
# flying_range = 254
# drone_1 = Drones(flying_range)
# drone_1.load_packages(8)
# drone_1.deliver(drone_1.package[0].index, 25)
#
# dck_hub = Docking_hubs(12, flying_range)
# print("docking hub index: ", dck_hub.index)
# drone_1.reserve(dck_hub.index)
# print(drone_1.pack_res_list)
# print(drone_1.get_pack_reservation())
# print(drone_1.battery.left_ba_sta)
# drone_1.battery_changed()
# print(drone_1.battery.left_ba_sta)
# print(drone_1.reserve_battery(dck_hub.index))
# print(drone_1.get_bat_reservation())



