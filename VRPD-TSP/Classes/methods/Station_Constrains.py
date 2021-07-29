#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.Batteries import Batteries
from Classes.Depot import Depot
from Classes.Docking_hubs import Docking_hubs
from Classes.Drones import Drones
from Classes.Minivan import Minivan
from Classes.Resources import Resources
from Classes.Vehicles import Vehicles
from Classes.methods.Constrains import Constrains
from Classes.methods.Drone_Constrains import Drone_Constrains
from Classes.methods.Van_Constrains import Van_Constrains
from Classes.Routes import Routes


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

class Depot_Constrains(Constrains):
    def __init__(self, routes: Routes = Routes(), vehicles: Vehicles = Vehicles()):
        """
        the class who is the spot that the vehicles start to deliver
        :param routes: the class to manage docking hubs, depot and customer nodes
        :param vehicles: the class to manage deliver vehicles: a minivan and two drones as default
        """
        self.routes: Routes = routes
        self.routes.init_graph_nodes()

        self.depot: Depot = self.routes.nodes_depot

        self.docking_hubs: list[Docking_hubs] = self.routes.nodes_docking_hubs
        self.dockhub_constrains: list[DockingHub_Constrains] = [DockingHub_Constrains(self.docking_hubs[i])
                                                                for i in range(len(self.docking_hubs))]

        self.vehicle: Vehicles = vehicles
        # self.vehicle.init_sets()
        self.van_constrains: Van_Constrains = Van_Constrains(self.vehicle)
        self.drones: list[Drone_Constrains] = [Drone_Constrains(self.vehicle.drones[i])
                                               for i in range(len(self.vehicle.drones))]

        self.resources: Resources = Resources()
        self.resources.collect_overall_resources(self.vehicle.minivan, self.vehicle.drones,
                                                 self.docking_hubs)

