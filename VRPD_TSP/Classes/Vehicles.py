#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.Drones import Drones
from Classes.Minivan import Minivan

class Vehicles:
    def __init__(self):
        self.minivan: Minivan = None
        self.drones: list[Drones] = list()
        self.vehicle_set: dict = {"Minivan": self.minivan, "Drones": self.drones}

    def __eq__(self, other):
        return self.minivan == other.minivan & self.drones[0] == other.drones[0] & self.drones[1] == other.drones[1]

    def init_sets(self, minivan: Minivan = Minivan(),
                  drones: list = [Drones() for i in [0, 1]], drone_pack_num: int = 5):
        self.minivan = minivan
        self.drones = drones
        [self.drones[i].load_packages(drone_pack_num) for i in range(len(self.drones))]
        self.vehicle_set: dict = {"Minivan": self.minivan, "Drones": self.drones}

 