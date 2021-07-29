#!/usr/bin/python
# -*- coding: UTF-8 -*-

from Classes.PARAMs import initial_temp, final_temp, alpha, obj_threshold
class SA_Model:
    def __init__(self, initial_state):
        self.initial_temp = initial_temp
        self.final_temp = final_temp
        self.alpha = alpha
        self.initial_state = initial_state
        self.current_state = self.initial_state
        self.current_temp = self.initial_temp

        self.obj_threshold = obj_threshold

    def get_current_state(self):
        return self.current_state

    def set_current_state(self, current):
        self.current_state = current

    def get_current_temp(self):
        return self.current_temp

    def change_current_temp(self):
        self.current_temp -= self.alph

    def set_current_temp(self, current_tp):
        self.current_temp = current_tp

    def get_alph(self):
        return self.alpha

    def set_alph(self, alph):
        self.alpha = alph

