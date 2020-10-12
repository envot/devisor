#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

class ConnectionClass():
    def __init__(self, devisor, address='smbus,1,0x20,A0'):
        self.devisor = devisor 
        addressArray = address.split(',')
        self.bank = addressArray[3][0]
        self.channel = int(addressArray[3][1])
        self.con = self.devisor.runningConnections.open(
                'mcp23017,'+','.join(addressArray[:-1]))
        self.con.write_bit('IODIR'+self.bank,
                self.channel, False)

    def write(self, value):
        return self.con.write_bit('GPIO'+self.bank,
                        self.channel,
                        value)
