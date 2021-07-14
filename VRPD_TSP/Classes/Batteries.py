#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
from Classes.PARAMs import flying_range_drone

class Batteries:
    def __init__(self, flying_range: int = flying_range_drone):
        """
        presents the batteries of drones
        :param flying_range: int, the maximum distance of drone can fly
        """
        self.index = "bat_"+str(uuid.uuid1())[:10]
        self.max_ba: int = flying_range
        self.left_ba_sta: float = self.max_ba
    #    self.rec_ba_res_num: int = 0
    #    self.ba_res_list: list = list()

    def charge_overnight(self):
        self.left_ba_sta: int = self.max_ba

    def use_battery(self, w: float):
        """
        used battery of every delivery
        :param w: the distance the drone has flied
        """
        self.left_ba_sta = self.left_ba_sta - w

    def __index__(self):
        return self.index

