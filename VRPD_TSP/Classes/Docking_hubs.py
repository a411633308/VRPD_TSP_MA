#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
from Classes.Batteries import Batteries
from Classes.Packages import Packages
from Classes.PARAMs import max_bat_num_dockhub, flying_range_drone, max_pack_num_dockhub
import random

class Docking_hubs:
    def __init__(self, num: int = max_bat_num_dockhub, flying_range: int = flying_range_drone,
                 stock_packages: int = max_pack_num_dockhub,
                 longtitude: int = random.sample(range(10, 50), 1), latitude: int = random.sample(range(20, 60), 5)):
        """
        Docking hub nodes, which has default packages number 20 packages
        :param num: the number of batteries can be saved in this docking hub.
        :param flying_range: the maximum flying range of drone.
        """
        self.type: str = "docking hubs"
        self.index: str = "doc_"+str(uuid.uuid1())[:10]
        self.batteries: list = list()
        # self.packages: Packages = Packages()
        self.landed_drone_num: int = 0
        self.batteries_backup(num, flying_range)
        self.name_landed_drones: list = list()
        self.left_batteries_num = len(self.batteries)
        self.rec_pack_num: int = 0
        self.rec_bat_num: int = 0
        self.package_delivered: list = list()
        self.packages: list = [Packages() for i in range(stock_packages)]
        self.long: int = longtitude[0]
        self.lat: int = latitude[3]

    def __eq__(self, other):
        return self.index == other.index

    def __str__(self):
        a = "Docking hub " + self.index + " has still batteries " + \
            str(self.left_batteries_num) + " left"
        return a

    def __index__(self):
        return self.index

    # >--------------------functions for packages--------------------start
    def receive_packReservation(self):
        """
        get a package reservation from drone/minivan
        :return: 1
        """
        self.rec_pack_num += 1
        return 1

    def get_packReservation_received(self):
        return self.rec_pack_num

    def unload_to_drone(self, node: list):
        """
        pop all packages according to given list of customer needs from drones
        :param node:  given list of customer needs
        :return: 1
        """
        pack_index = [i for i in range(len(self.packages)) if
                      self.packages[i] == node[i]]
        print("found packages indexes are: ", pack_index)
        [self.packages.pop(pack_index[i]) for i in range(len(pack_index))]
        self.rec_pack_num = self.rec_pack_num - len(pack_index)
        return 1

    # <--------------------functions for packages--------------------end

    # >--------------------functions for batteries--------------------start
    def receive_batReservation(self):
        """
        get a package reservation from drone/minivan
        :return: 1
        """
        self.rec_bat_num += 1
        return 1

    def get_batReservation_received(self):
        return self.rec_bat_num

    def get_left_batteries(self):
        return self.left_batteries_num

    def batteries_backup(self, num: int, flying_range: int):
        """
        saves the list of batteries that have saved in the docking hub.
        :param num: the number of batteries.
        :param flying_range: the maximum energy of battery.
        """
        [self.batteries.append(Batteries(flying_range)) for i in range(num)]
        self.left_batteries_num = len(self.batteries)
        return self.batteries

    def change_battery(self):
        self.rec_bat_num -= 1
        self.left_batteries_num -= 1
        return 1

    # <--------------------functions for batteries--------------------end

    # >--------------------functions for drones--------------------start
    def land_drone(self, drone_nodes: str):
        """
        A drone lands at the docking hub.
        :param drone_nodes: str, index of drone
        :return: a description for logging.
        """
        self.landed_drone_num += 1
        self.name_landed_drones.append(drone_nodes)
        return 1

    def launch_drone(self, drone_nodes: str):
        """
        Launch drone with certain index
        :param drone_nodes: the index of drone launched
        :return: successfully 1, or 0.
        """
        drone_index = [i for i in range(self.landed_drone_num)
                       if self.name_landed_drones[i] == drone_nodes]

        if drone_index:
            self.package_delivered.append(drone_nodes)
            self.name_landed_drones.pop(drone_index[0])
            self.landed_drone_num -= 1
            return 1
        else:
            return 0

    def get_land_drones(self):
        """
        The drones have landed at the docking hub.
        :return: a description for logging.
        """
        return self.name_landed_drones
    # <--------------------functions for drones--------------------end


# flying_range = 352
# drone = Drones(flying_range)
# dock_hub = Docking_hubs(4, flying_range)
# dock_hub.land_drone(drone.index)
# a = dock_hub.get_land_drones()[0]
# print(type(a))
# print("drone's name", a)
# print("number of landed drones:", dock_hub.landed_drone_num)
# b = dock_hub.launch_drone(a)
# print("number of landed drones:", dock_hub.landed_drone_num)
# print("landed drones are:", dock_hub.get_land_drones())
