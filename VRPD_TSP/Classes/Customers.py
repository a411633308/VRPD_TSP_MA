#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid


class Customers:
    def __init__(self, pack_needs: int, non_flying: bool):
        """
        Customer
        :param param: dict,'pack_needs','non_flying'.
        """

        self.index = "cus_"+str(uuid.uuid1())[:10]
        self.pack_needs: list = pack_needs
        self.served: bool = False
        self.in_non_flying: bool = non_flying

    def __index__(self):
        return self.index

    def __eq__(self, other):
        return self.index == other.index

    def __str__(self):
        return "+"*12 + " Customer " + self.index + " lives in 'non flying range' " + str(self.in_non_flying) + "+"*12

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

