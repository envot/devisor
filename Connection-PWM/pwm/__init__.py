#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

class ConnectionClass():
    def __init__(self, devisor, address='pca9685,smbus,1,0x40,0'):
        self.devisor = devisor 
        addressArray = address.split(',')
        addressArray[0] = 'pwm'+addressArray[0]
        self.con = self.devisor.runningConnections.open(
                ','.join(addressArray))

    def set_pwm(self, value):
        return self.con.set_pwm(value)

    def set_phase(self, value):
        return self.con.set_phase(value)
