#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
class Packages:
    def __init__(self):
        """
            This class initiates the deliver tasks in a unit of days.
        """
        self.num_pack: int = 0
        self.rec_pack_res_num: int = 0
        self.index: str = str(uuid.uuid1())[:10]

    def __index__(self):
        return self.index

    def __str__(self):
        return "package: " + self.index

    def __index__(self):
        return self.index

    def __eq__(self, other):
        return self.index == other.index

    def set_deliver_tasks(self, num: int) -> str:
        """
        set the deliver tasks
        :param num: the given deliver tasks.
        :return: a description of tasks initiation for logging.
        """
        self.num_pack: int = num
        return 1

    def receive_reservation(self):
        """
        #Docking hubs/Minivans# receive packages
        :return: 1
        """
        self.rec_pack_res_num += 1
        return 1

    def get_reservation_received(self):
        """
        get the number of packages reservation from #docking hubs/minivans#
        :return: 1
        """
        return self.rec_pack_res_num

    def get_deliver_tasks(self):
        """
        return the current state of deliver tasks.
        :return: the number of deliver tasks.
        """
        return self.num_pack
#
# class Packages_Drone(Packages):
#     def __init__(self):
#         """
#             This class is the sub-object of packages for drone.
#         """
#         self.res_packages: list = list()
#         self.del_packages: list = list()
#         self.index = str(uuid.uuid1())[:10]
#         print("+"*12+"initiate the list of packages deliverd and reserved for drones"+"+"*12)
#
#     def reserve(self,res_node: str):
#         """
#             presents the activation of reservation by the drone.
#         :param res_node: str
#             saves the node's index that has received the package reservation of the drone.
#         :return: a description of this activation for logging
#         """
#         self.res_packages.append(res_node)
#         print("+"*12+"reserves packages successfully"+"+"*12)
#         return "+"*12+"reserves packages from" + str(self.res_packages)+"+"*12
#
#     def deliver(self,del_customer: str):
#         """
#             demonstrates the activation for each delivery of the drone.
#         :param del_customer: str
#             the customer node that has delivered by the drone.
#         :return: a description of this activation for logging
#         """
#         self.del_packages.append(del_customer)
#         return "+"*12+"deliver package for customer" + del_customer+"+"*12
#
#     def get_res_list(self):
#         """
#             return the nodes list that receive the drone's package reservation.
#         :return: the list of nodes that receive the drone's package reservation.
#         """
#         return self.res_packages
#
#     def get_del_list(self):
#         """
#             return the current state of packages delivered by the drone.
#         :return: the packages delivered by the drone.
#         """
#         return self.res_packages
#
#     def __index__(self):
#         return self.index
#
# class Packages_Minivan(Packages):
#     def __init__(self):
#         """
#         demonstrates the packages that are included in the minivans.
#         """
#         self.index = str(uuid.uuid1())[:10]
#         self.res_packages: list = list()
#         self.del_packages: list = list()
#         self.rec_packages: int = 0  # packages reservation received
#
#     def reserve(self,res_node: str):
#         """
#             presents the activation of reservation by the truck.
#         :param res_node: str
#             saves the node's index that has received the package reservation of the minivan.
#         :return: a description of this activation for logging.
#         """
#         self.res_packages.append(res_node)
#         print("+"*12+"reserves packages successfully"+"+"*12)
#         return "+"*12+"reserves packages from" + str(self.res_packages)+"+"*12
#
#     def deliver(self,del_customer: str):
#         """
#             demonstrates the activation for each delivery of the minivan.
#         :param del_customer: str
#             the customer node that has delivered by the minivan.
#         :return: a description of this activation for logging.
#         """
#         self.del_packages.append(del_customer)
#         return "+"*12+"deliver package for customer" + del_customer+"+"*1
#
#     def receive_reservation(self):
#         self.rec_packages += 1
#         print("+"*12+'The minivan receives a package reservation from a drone.'+"+"*12)
#
#     def uploaded_to_drone(self):
#         self.rec_packages -= 1
#         print("+"*12+'The minivan unloads a package reservation to a drone.'+"+"*12)
#
#     def __index__(self):
#         return self.index
#
# class Packages_DockingHubs(Packages):
#     def __init__(self):
#         """
#             Subclass of Packages for docking hub nodes.
#         """
#
#         self.index: str = str(uuid.uuid1())[:10]
#         self.res_packages: int = 0
#
#     def reserved(self):
#         """
#             receive a package reservation from drone/minivan.
#         :return: a description for logging.
#         """
#         self.res_packages += 1
#         print("+"*12+"reserves packages successfully"+"+"*12)
#         return "+"*12+"reserves packages from" + str(self.res_packages)+"+"*12
#
#     def unload(self):
#         self.res_packages -= 1
#         print("+"*12+"Packages unloaded successfully"+"+"*12)
#         return "+"*12+"Packages unloaded successfully"+"+"*12
#
#     def get_res_num(self):
#         """
#             the number of package reservation received from drone/minivan.
#         :return: the number of packages reserved.
#         """
#         return self.res_packages
#

