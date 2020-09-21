#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import os

availableConnections = []
filenames = os.listdir('./devisor/connections')
for i,filename in enumerate(filenames):
    if filename[-3:] == '.py' and not filename in ['__init__.py', 'connections.py']:
        availableConnections.append(filename[:-3])

class Connections():
    def __init__(self, devisor):
        self.devisor = devisor
        self.opened = {}
        self.available = availableConnections

    def open(self, address):
        if not address in self.opened:
            self.opened[address] = self._add(address)
        return self.opened[address]

    def _add(self, address):
        for ava in self.available:
            if ava == address[:len(ava)]:
                return self._start(address)
        raise Exception('Connection address not available.')

    def _start(self, address):
        addressArr = address.split(',')
        condev = devisor_import(addressArr[0], 'connection')
        newDevice= condev.ConnectionClass(self.devisor, ','.join(addressArr[1:]))
        return newDevice
