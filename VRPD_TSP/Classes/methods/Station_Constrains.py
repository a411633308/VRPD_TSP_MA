#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.methods.Constrains import Constrains
from Classes.Batteries import Batteries
from Classes.Drones import Drones
# from Classes.Packages import Packages
from Classes.Minivan import Minivan
# from Classes.Vehicles import Vehicles
from Classes.Docking_hubs import Docking_hubs
from Classes.Depot import Depot
from Classes.Vehicles import Vehicles

class Depot_Constrains(Constrains):
    def __init__(self, depot: Depot):
        self.depot: Depot = depot
        self.vehicle: Vehicles = Vehicles()

class DockingHub_Constrains(Constrains):
    def __init__(self, docking_hub: Docking_hubs):
        self.docking_hub: Docking_hubs = docking_hub
        self.minivans: list[Minivan] = list()  # the list to save minivans landed at the docking hub
        self.drones: list[Drones] = list()  # the list to save drones landed at the docking hub
        self.batteries: list[Batteries] = self.docking_hub.batteries  # batteries saved at the docking hub
        self.max_batteries = len(self.batteries)  # the maximum batteries can be saved here
        self.left_batteries: int = len(self.batteries)
        self.given_batteries: list[str] = list()

    def change_battery(self, right_locate: bool):
        """
        change the battery on the drone, who has landed at the docking hub
        :return: successfully, the fist battery in the backup; unsuccessfully, 0.
        """
        if self.left_batteries > 0 and len(self.batteries) != 0 and right_locate:
            self.given_batteries.append(self.batteries[0].index)
            batter = self.batteries[0]
            self.batteries.pop(0)
            return batter
        else:
            return 0

    def land_drones(self, drone: Drones):
        self.drones.append(drone)
        return 1

    def land_minivan(self, minivan: Minivan):
        self.minivans.append(minivan)
        return 1

