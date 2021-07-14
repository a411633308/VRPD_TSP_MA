#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.methods.Constrains import Constrains
from Classes.Batteries import Batteries
from Classes.Drones import Drones
# from Classes.Packages import Packages
from Classes.Minivan import Minivan
from Classes.Vehicles import Vehicles
import math

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
        if self.left >= 1:

            self.weight.append(drone_index)  # add the index of drone who has got the full-charged battery

            # find the related drone that have landed on the van
            related_drone = [i for i in range(len(self.drone)) if self.drone[i].index == drone_index]

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


class Van_Constrains:
    def __init__(self, vehicle: Vehicles):
        self.minivan: Minivan = vehicle.vehicle_set['Minivan']
        self.drones: list = vehicle.vehicle_set['Drones']
        self.van_batteries: Van_Batteries = Van_Batteries(self.minivan, self.drones)
        self.van_fuel: Constrains = Constrains(self.minivan.max_range)
        self.van_packages: Van_Packages = Van_Packages(self.minivan)

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
        if self.minivan.rec_bat_res_num >= 1:
            batter = self.van_batteries.change(drone_index=drone_index)
            if batter != 0:
                return batter
            else:
                return 0
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
        :param cus_needs: str,
        the index of packages that is the required needs of customer.
        :param w: int,
        the fuel costs for this deliver
        :return: successfully, 1; unsuccessfully, 0.
        """
        if self.van_fuel.left >= w*2 + closet_dckh:
            self.van_fuel.change(w)
            self.minivan.deliver(w)
            self.van_fuel.left = self.minivan.left_fuel
            return 1
        else:
            return 0

    def receive_packages_reservation(self):
        """
        If deliver through packages indexes, the reservation of packages is required.
        :param drone_list: index of drone who want to reserve packages from the van
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
        if self.van_packages <= 0 & self.van_fuel > closet_dckh*2 + closet_cus:
            self.minivan.reserve(node)
            return 1
        else:
            return 0

    def load_packages(self, load_rate: float, closet_dckh: float):
        """
        reload packages onto the van with a certain rate, load_rate
        :param load_rate: the rate between load weight and the distance it can still run
        :param closet_dckh: the distance cost for the van to get the closet docking hub node.
        :return: successfully, 1; unsuccessfully, 0.
        """
        if self.van_fuel > 2*closet_dckh:
            num: int = math.floor(self.van_fuel.left*load_rate)  # get the integer according to the left fuel
            self.minivan.load_packages(num)
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


from Classes.Vehicles import Vehicles
from Classes.Routes import Routes
# two kinds of class for the STP-D, nodes and vehicles
# -------------- 1.initiate the classes of routes and vehicles
route = Routes()  # customer, depot and docking hubs nodes
route.init_graph_nodes()

vehicle = Vehicles()  # two drones and a minivan are a set of mother ship system
vehicle.init_sets()  # initiate the three vehicles according to the default parameters


from Classes.Resources import Resources
resources = Resources()
resources.collect_overall_resources(minivan=vehicle.minivan, drones=vehicle.drones,dck_hubs=route.nodes_docking_hubs)

ab_c = Van_Constrains(vehicle)  # according to the initial classes, check whether they satisfy certain constrains

# -------------- 2.the constrains for the system to finish the tasks like deliver packages, change battery, etc
# drone_1, that leaves the minivan and do the delivery tasks
drone_1 = vehicle.drones[0]
print(drone_1.package)
drone_1.deliver(drone_1.package[0].index, 26)
drone_1.deliver(drone_1.package[0].index, 26)
drone_1.deliver(drone_1.package[0].index, 26)
drone_1.deliver(drone_1.package[0].index, 26)
(len(drone_1.package))

vehicle.drones[0].reserve_battery(vehicle.minivan.index)
a = ab_c.change_battery(drone_index=vehicle.drones[0].index)  # whether change battery of certain drone satisfy the relevant constrains
# depart from the depot node, the load on the drones are emtpy, only when the
# ab_c.unload_to_drone()


