#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import os
from ..devisorbase import devisor_import

class Connections():
    def __init__(self, devisor):
        self.devisor = devisor
        self.opened = {}

    def open(self, address):
        if not address in self.opened:
            self.opened[address] = self._start(address)
        return self.opened[address]

    def _start(self, address):
        addressArr = address.split(',')
        condev = devisor_import(self.devisor, addressArr[0], 'connection')
        newDevice = condev.ConnectionClass(self.devisor, ','.join(addressArr[1:]))
        return newDevice
