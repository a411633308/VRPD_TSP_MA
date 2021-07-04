#!/usr/bin/python
# -*- coding: UTF-8 -*-
import uuid

class Depot:
    def __init__(self):
        self.index = "dep_"+str(uuid.uuid1())[:10]

    def __index__(self):
        return self.index

    def pack_trucks(self):
        return 1

    def launch_trucks(self):
        return 1

