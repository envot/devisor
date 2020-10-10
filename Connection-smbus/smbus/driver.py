#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import smbus

class ConnectionClass():
    def __init__(self, devisor, address="1"):
        self.devisor = devisor
        self.bus = smbus.SMBus(int(address))
