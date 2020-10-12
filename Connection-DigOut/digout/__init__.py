#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

class ConnectionClass():
    def __init__(self, devisor, address='mcp23017,smbus,1,0x20,A0'):
        self.devisor = devisor 
        addressArray = address.split(',')
        addressArray[0] = 'digout'+addressArray[0]
        self.con = self.devisor.runningConnections.open(
                ','.join(addressArray))

    def write(self, value):
        return self.con.write(value)
