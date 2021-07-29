#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.methods.Constrains import Constrains
from Classes.Batteries import Batteries
from Classes.Drones import Drones
from Classes.Packages import Packages
from Classes.Minivan import Minivan
from Classes.Vehicles import Vehicles
import random
import math
# from Classes.PARAMs import rate_load_range_van, rate_load_pack_van

class Van_Batteries(Constrains):
    # @Constrains.abstractmethod
    def __init__(self, minivan: Minivan, drone: list):
        """
        manage the battery constrains on the van
        :param minivan: the class of minivan in this single salesman traveling problem
        """
        self.drone: list[Drones] = drone  # the drones that have landed on the van
        self.minivan: Minivan = minivan  # the minivan
        self.batteries: list[Batteries] = minivan.batteries  # the list of batteries that have saved on the van
        self.max: int = self.minivan.max_bat_num  # the maximum batteries number that can save on the van
        self.left: int = self.minivan.left_bat_num  # the levt batteries number on the van
        self.weight: list = list()  # the indexes of drones who have got a packages from the van
        self.used_batteries: list = list()  # the used batteries on the van

    def change(self, drone_index: str):
        """
        change the first battery from the battery list to the drone
        :param drone_index: the drone who needs to get a new battery
        :return: successfully, the battery who will be changed onto the drone; unsuccessfully, 0
        """
        if self.left > 0:
            print(drone_index)
            self.weight.append(drone_index)  # add the index of drone who has got the full-charged battery
            # find the related drone that have landed on the van
            related_drone = [i for i in range(len(self.drone)) if self.drone[i].index == drone_index]
            print("found battery drone index on the van", related_drone)
            # if the related drone is already landed at the van, then change its battery
            if len(related_drone) != 0:
                related_drone = related_drone[0]
                self.used_batteries.append(self.drone[related_drone].battery)  # the index of batteries changed from the drone
                # change the battery left on the van
                batter = self.minivan.change_batteries()
                # update the battery state on the drone
                self.drone[related_drone].battery_changed(batter)

                # update the batteries on the van constrains.
                self.batteries = self.minivan.batteries  # delete the battery given from the battery list
                self.left = len(self.batteries)  # update the left batteries number currently
                return batter
            else:
                return 0
        else:
            return 0


class Van_Packages(Constrains):
    # @Constrains.abstractmethod
    def __init__(self, minivan: Minivan):
        """
        The constrains of the packages on the van.
        :param minivan:
        """
        self.minivan: Minivan = minivan
        self.packages: list[Packages] = self.minivan.packages
        self.max = self.minivan.max_packages_num
        self.left = self.max
        self.weight = None

    def change(self, cus_index: str, w: float):
        """
        This van deliver a package by itself
        :param cus_index: the index of package that the customer required
        :param w: the fuel cost for the minivan to deliver the package
        :return: successfully, the left packages in the van; unsuccessfully, 0
        """
        if self.left >= 1:
            self.weight.append(cus_index)
            self.minivan.deliver(cus_index, w)
            self.left = self.minivan.left_pack
            return self.left
        return 0

    def reset(self):
        """
        judge whether the left package is empty or not
        :return: yes, recall reload() function; no, return 0
        """
        if self.left < 1:
            # [self.packages.append(Packages()) for i in range(self.max-self.left)]
            self.minivan.load_packages()  # reload packages from the docking hubs
            self.left = len(self.minivan.packages)  # restates the number of left packages
            return self.left
        else:
            return 0

    def deliver(self, w: float):
        """
        :param w:
        :return: return the left fuel of the minivan
        """
        self.weight.append(self.minivan.packages[0])
        self.minivan.deliver(w=w)
        self.packages = self.minivan.packages
        return self.minivan.left_fuel


class Van_Constrains:
    def __init__(self, vehicle: Vehicles):
        self.drones_num: int = len(vehicle.drones)
        self.minivan: Minivan = vehicle.vehicle_set['Minivan']
        self.drones: list = vehicle.vehicle_set['Drones']
        self.van_batteries: Van_Batteries = Van_Batteries(self.minivan, self.drones)
        self.van_fuel: Constrains = Constrains(self.minivan.max_range)
        self.van_packages: Van_Packages = Van_Packages(self.minivan)
        self.cost_rate: float = random.uniform(1, 1.3)
        self.route: list[str] = list() # whether there's necessary to save its cover route or not.
        # self.pack_load_rate: float = rate_load_range_van
        # self.load_rate: float = rate_load_pack_van

# -----------------------functions for battery constrains-----------------------
    def change_battery(self, drone_index: str):
        """
        If (1)the drone who reserves the battery arrives at the minivan, (2) the battery reservation number of this van
        is larger than or equal to 1, the first object of the battery list will be deleted from the minivan, and as the
        return object of this function.
        whether the drone who has reserved a battery from the minivan has arrived at the minivan or not?
        :param drone_index: str,
        the index of drone who reserved a battery from the minivan
        :return: successfully changed, the battery for the drone; unsuccessfully, 0.
        """
        drone_ = [i for i in range(len(self.drones)) if self.drones[i].index == drone_index]
        print("left batteries and found drone_index: ", len(drone_), self.van_batteries.left)
        if len(drone_) != 0 and self.van_batteries.left >= 1:
            print(" whether this branch is ran", self.drones[drone_[0]].index)
            batter = self.van_batteries.change(drone_index=self.drones[drone_[0]].index)
            return batter
        else:
            return 0

    def receive_battery_reservation(self):
        """
        If the left battery is not empty, then receive the battery reservation.
        :return: successfully, 1; unsuccessfully, 0.
        """
        if self.van_batteries.left > 0:
            self.minivan.receive_bat_reservation()
            return 1
        else:
            return 0

    # -----------------------functions for battery constrains-----------------------

    # -----------------------functions for fuel and packages constrains-----------------------
    def deliver_packages(self, w: float, closet_dckh: float):
        """
        The van must have more fuel than delivering the packages at first and then come back to this node, go to
        the closet docking hub node, and then pack.
        :param closet_dckh: float,
        the fuel costs for the van to the closet docking hub node
        the index of packages that is the required needs of customer.
        :param w: int,
        the fuel costs for this deliver
        :return: successfully, 1; unsuccessfully, 0.
        """
        if self.van_fuel.left >= w * 2 + closet_dckh:
            left_fuel = self.van_packages.deliver(w)
            self.van_fuel.left = left_fuel
            self.van_fuel.weight.append(w)
            self.minivan.deliver(w*self.cost_rate)
            self.van_fuel.left = left_fuel
            return 1
        else:
            return 0

    def receive_packages_reservation(self):
        """
        If deliver through packages indexes, the reservation of packages is required.
        :return: successfully, 1; unsuccessfully, 0.
        """
        if self.van_packages.left > 2:
            self.minivan.receive_pack_reservation()
            return 1
        else:
            return 0

    def reserve_packages_from_docking_hubs(self, node: str, closet_dckh: float, closet_cus: float):
        """
        If the van's left fuel are able to support loading packages from the closet docking hubs and deliver the
        packages to the closet customer.
        :param node: the index of docking hub who receives the van's package reservation.
        :param closet_dckh: the weight of the van to the closet docking hub node
        :param closet_cus: the weight of the van to the closet customer node
        :return: successfully, 1; unsuccessfully, 0.
        """
        if self.van_packages <= 0 & self.van_fuel > closet_dckh * 2 + closet_cus:
            self.minivan.reserve(node)
            return 1
        else:
            return 0

    def load_packages(self, closet_dckh: float):
        """
        reload packages onto the van with a certain rate, load_rate
        :param load_rate: the rate between load weight and the distance it can still run
        :param closet_dckh: the distance cost for the van to get the closet docking hub node.
        :return: successfully, 1; unsuccessfully, 0.
        """
        if self.van_fuel > 2 * closet_dckh:
            num: int = math.floor(self.van_fuel.left * self.load_rate)  # get the integer according to the left fuel
            self.minivan.load_packages(num)
            self.van_fuel.left = self.van_fuel.left
            return 1
        else:
            return 0

    def unload_to_drone(self, node: list):
        """
        unload the packages to the drone, if the left packages on the van are enough for they both.
        :param node:
        :return: successfully, 1 ; unsuccessfully, 0.
        """
        if self.van_packages.left > 1:
            self.minivan.unload_to_drone(node)
            self.van_fuel.left = self.minivan.left_fuel
            return 1
        else:
            return 0

    # -----------------------functions for fuel and packages constrains------------------------

    # -----------------------functions for drones landed on the van constrains------------------------
    def land_drones(self, drone: Drones):
        if self.drones_num > len(self.drones):
            self.drones.append(drone)
            return 1
        else:
            return 0

    def launch_drone(self, drone_index: str):
        drone_ = [i for i in range(len(self.drones)) if self.drones[i].index == drone_index]
        try:
            self.drones.pop(drone_[0])
            return 1
        except IndexError:
            return 0

    def stop_van(self, closet_dockinghub: float, closet_customer: float):
        if self.van_fuel.left <= 2 * closet_customer + closet_dockinghub:
            return self.minivan
        else:
            return 0
    # -----------------------functions for drones landed on the van constrains------------------------


# from Classes.Resources import Resources
# from Classes.Vehicles import Vehicles
# from Classes.Routes import Routes
#
# # two kinds of class for the STP-D, nodes and vehicles
# # -------------- 1.initiate the classes of routes and vehicles
# route = Routes()  # customer, depot and docking hubs nodes
# route.init_graph_nodes()
#
# vehicle = Vehicles()  # two drones and a minivan are a set of mother ship system
# vehicle.init_sets()  # initiate the three vehicles according to the default parameters
#
# [print(" Drones on the van: ", vehicle.drones[i].index) for i in range(len(vehicle.drones))]
#
# resources = Resources()
# resources.collect_overall_resources(minivan=vehicle.minivan, drones=vehicle.drones, dck_hubs=route.nodes_docking_hubs)
#
# ab_c = Van_Constrains(vehicle)  # according to the initial classes, check whether they satisfy certain constrains
# from Classes.methods.Drone_Constrains import Drone_Constrains
# drone_constrains: list = [Drone_Constrains(ab_c.drones[i]) for i in range(len(ab_c.drones))]
#
# ab_c.launch_drone(ab_c.drones[0].index)
#
# # -------------- 2.the constrains for the system to finish the tasks like deliver packages, change battery, etc
# # drone constrains
#
# drone_1 = drone_constrains[0]
# # print(drone_1.drone_index)
# # print("left packages number and battery state of the drone: ", drone_1.drone_packages.left,
# #       drone_1.drone_batteries.left)
# # drone_1.deliver_package(
# #     26)  # although the deliver costs of each package is integer but the load weight of the drone decreases
# # # its left battery state increases simutaniously.
# print("1. deliver, left packages number and battery state ", drone_1.drone_packages.left, drone_1.drone_batteries.left)
# drone_1.deliver_package(26)
# print("2. deliver, left packages number and battery state ", drone_1.drone_packages.left, drone_1.drone_batteries.left)
# drone_1.deliver_package(26)
# print("3. deliver, left packages number and battery state ", drone_1.drone_packages.left, drone_1.drone_batteries.left)
# drone_1.deliver_package(26)
# print("4. deliver, left packages number and battery state ", drone_1.drone_packages.left, drone_1.drone_batteries.left)
#
# battery = ab_c.change_battery(
#     drone_index=ab_c.drones[0].index)  # whether change battery of certain drone satisfy the relevant constrains
# print("battery that will be changed onto the drone: ", battery)
# drone_1.change_battery(ab_c.van_batteries.left, 30, battery)
# drone_1.load_packages()
# landed_drone = drone_1.stop_drone(0, 50)
# ab_c.land_drones(landed_drone)
#
# ab_c.stop_van(60,500)