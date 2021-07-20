#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid
import random

class Depot:
    def __init__(self, longtitue: int = random.sample(range(20, 40), 1), latitude: int = random.sample(range(40, 60), 1)):
        self.index: str = "dep_"+str(uuid.uuid1())[:10]
        self.type: str = "depot"
        self.long: int = longtitue[0]
        self.lat: int = latitude[0]

    def __index__(self):
        return self.index

    def pack_trucks(self):
        return 1

    def launch_trucks(self):
        return 1

