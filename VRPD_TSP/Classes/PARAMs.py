#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

flying_range_drone: float = 65
max_range_van: float = 300
rate_load_range_drone: float = random.uniform(0, 0.1)  # how many packages should be loaded according to the left energy
rate_load_range_van: float = random.uniform(0.3, 0.5)
rate_load_pack_drone: float = random.uniform(0.1, 0.2)  # how much !a package! affects its left battery state
rate_load_pack_van: float = random.uniform(0.3, 0.5)

max_pack_num_van: int = 20
max_pack_num_dockhub: int = 50

max_bat_num_van: int = 2
max_bat_num_dockhub: int = 5
