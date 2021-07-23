#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
import random

class Depot:
    def __init__(self, longtitue: int = random.sample(range(10, 50), 1),
                 latitude: int = random.sample(range(20, 60), 1)):
        self.index: str = "dep_"+str(uuid.uuid1())[:10]
        self.type: str = "depot"
        self.long: int = longtitue[0]
        self.lat: int = latitude[0]
        self.wind_direction: int = random.choice([1,-1])

    def __index__(self):
        return self.index

    def pack_trucks(self):
        return 1

    def launch_trucks(self):
        return 1

