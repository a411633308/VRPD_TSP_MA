#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid

class Weather:
    def __init__(self):
        """
        The weather effects the flying range of drone positively or negatively
        """
        self.suit:bool = True
        self.wind_speed:int = 0
        self.index = str(uuid.uuid1())[:10]

    def set_wea_drone(self, suit):
        """
        set whether the weather is suitable for drone delivery
        :param suit: bool"""
        self.suit = suit

    def get_wea_drone(self):
        """
        get whether the weather is suitable for drone delivery
        :return:"""
        return self.suit

    def set_wind_speed(self, speed):
        """
        set the speed of the wind
        :param speed: int"""
        self.wind_speed = speed

    def get_wind_speed(self):
        """
        return the speed of wind
        :return: int
        """
        return self.wind_speed

    def __index__(self):
        return self.index