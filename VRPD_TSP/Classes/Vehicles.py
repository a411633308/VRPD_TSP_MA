#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.Drones import Drones
from Classes.Minivan import Minivan
from Classes.PARAMs import drones_num_on_van, van_num, default_drone_pack_num

class Vehicles:
    """
    A class to manage a set of deliver vehicles: minivans and drones
    """
    def __init__(self):
        """
        initiate the class
        """
        self.minivan: Minivan = None
        self.drones: list[Drones] = list()
        self.vehicle_set: dict = {"Minivan": self.minivan, "Drones": self.drones}

    def __eq__(self, other):
        """
        compare whether two vehicles objects contains the same sub-objects
        :param other:
        :return: True or not
        """
        return self.minivan == other.minivan & self.drones[0] == other.drones[0] & self.drones[1] == other.drones[1]

    def init_sets(self, minivan: Minivan = Minivan(),
                  drones: list = [Drones() for i in range(drones_num_on_van)],
                  drone_pack_num: int = default_drone_pack_num):
        """
        A necessary function for the class to initiate all vehicles needed.
        :param minivan:
        :param drones:
        :param drone_pack_num: the number of drones that will be loaded on the drone
        :return:
        """
        self.minivan = minivan
        self.drones = drones
        [self.drones[i].load_packages(drone_pack_num, True) for i in range(len(self.drones))]
        self.vehicle_set: dict = {"Minivan": self.minivan, "Drones": self.drones}

 