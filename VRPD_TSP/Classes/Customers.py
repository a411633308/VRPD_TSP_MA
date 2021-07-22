#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
import random

class Customers:
    def __init__(self, pack_needs: int = 1, non_flying: bool = False,
                 longtitude: int = random.sample(range(10, 50), random.randint(0, len(range(10, 50)))),
                 latitude: int = random.sample(range(20, 60), random.randint(0, len(range(50, 80))))):
        """
        Customer
        :param param: dict,'pack_needs','non_flying'.
        """

        self.index = "cus_"+str(uuid.uuid1())[:10]
        self.type = "customers"
        self.pack_needs: int = pack_needs
        self.required_pack_list: list[str] = list()
        self.served: bool = False
        self.in_non_flying: bool = non_flying
        self.long: int = longtitude
        self.lat: int = latitude

    def __index__(self):
        return self.index

    def __eq__(self, other):
        return self.index == other.index

    def __str__(self):
        return "+"*12 + " Customer " + self.index + " lives in 'non flying range' " + str(self.in_non_flying) + "+"*12

    def require_certain_packages(self, pack_list: list):
        """
        initiates the customers' needs from given packages in the network
        :param pack_list: given packages required for the customer
        :return: if his needs equals to the his relevant packages indexes, 1; else 0
        """
        self.required_pack_list = pack_list
        if len(self.required_pack_list) == self.pack_needs:
            return 1
        else:
            return 0

    def receive_pack(self, node: str):
        """
        be recalled when customer receives package,
        when all needs are all covered, the customer has been served.
        :return:1
        """
        pack_index = [i for i in range(len(self.pack_needs)) if
                      self.pack_needs[i] == node]
        self.pack_needs.pop(pack_index[0])
        if len(self.pack_needs) == 0:
            self.served = True
        return 1

    def live_in_non_flying(self, live_in: bool):
        self.in_non_flying = live_in
        return 1

    def get_live_location(self):
        return self.in_non_flying


#
# param = {
#     'lon': 258,
#     'lat': 25.2,
#     'pack_needs': ['de0fd3f2d-e'],
#     'non_flying': False,
# }
# cus_1 = Customers(param)
# a = cus_1.receive_pack('de0fd3f2d-e')
# cus_1.live_in_non_flying(True)
# print(cus_1.get_location())

