#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

class ConnectionClass():
    def __init__(self, devisor, address='smbus,1,0x40,0'):
        self.devisor = devisor 
        addressArray = address.split(',')
        self.channel = int(addressArray[-1])
        self.con = self.devisor.runningConnections.open(
                'pca9685,'+','.join(addressArray[:-1]))
        self.resolution = 12
        self.phase = 0.
        self.value = 0.

    def set_pwm(self, value):
        self.value = value
        self.set_pwm_raw()

    def set_phase(self, phase):
        self.phase = phase
        self.set_pwm_raw()

    def set_pwm_raw(self):
        start = self._convert_value(phase)
        end = start + self._convert_value(self.value)
        return self.con.set_pwm_raw(self.channel, start, end)

    def _convert_value(self, value):
        return value/100*(2**self.resolution-1) % 2**self.resolution
