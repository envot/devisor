#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
import usbtmc

class ConnectionClass():
    def __init__(self, devisor, address='0x699,0x03a2'):
        self.devsor = devisor 
        self.address = address
        addressArray = address.split(',')
        if len(addressArray)>1:
            try:
                self.vendor = int(addressArray[0])
            except:
                self.vendor = int(addressArray[0],16)
            try:
                self.product = int(addressArray[1])
            except:
                self.product = int(addressArray[1],16)
        else:
            self.vendor = 0x0699
            self.product = 0x03a2
        serial = address.split(';')[-1]
        if len(serial) == 7 and serial[0] == 'C':
            self.serial = self.address.split(';')[-1]
            self.instr = usbtmc.Instrument(self.vendor,self.product,serial)
        else:
            self.instr = usbtmc.Instrument(self.vendor,self.product)
            self.serial = None

    def write(self, value):
        return self.instr.write(value)

    def ask(self, value):
        return self.instr.ask(value)
