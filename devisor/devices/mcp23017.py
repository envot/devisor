#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import sys
import time

from devisor.devisorbase import DeviceBase
from devisor.connections.mcp23017 import BANKS,CHANNELS


initNodes = {}

control = {
    'refresh-interval': {
        'valueInit' : 5.,
        'brokerInit' : True,
        'format' : "0.1:100",
        'settable' : True,
        'unit': 's',
        }
}

def invert_func(pB):
    pB.dev.mcp23017.write_register(pB.dev.mcp23017.registerNames['IPOL'+pB.name[-1]], pB.value)

def direction_func(pB):
    pB.dev.mcp23017.write_register(pB.dev.mcp23017.registerNames['IODIR'+pB.name[-1]], pB.value)

functions = [invert_func, direction_func]

for i,name in enumerate(['invert', 'direction']):
    for bank in BANKS:
        control[name+'-'+bank] = {
            'valueInit' : '00000000',
            'broker_func' : functions[i],
            'brokerInit' : True,
            'settable' : True,
            }
initNodes['control'] = control


def gpio_function(pB):
    channel = int(pB.name[-1])
    bank = pB.param.split('/')[-2][-1]
    if not pB.dev.mcp23017.read_bit(
                    pB.dev.mcp23017.registerNames['IODIR'+bank],
                channel):
        pB.dev.mcp23017.write_bit(
                pB.dev.mcp23017.registerNames['GPIO'+bank], channel, pB.value)
    else:
        pB.device(pB.dev.mcp23017.read_bit(
            pB.dev.mcp23017.registerNames['GPIO'+bank], channel))

gpioDict = {
        'valueInit' : False,
        'broker_func' : gpio_function,
        'brokerInit' : True,
        'settable' : True,
}

for bank in BANKS:
    bankDict= {}
    for channel in CHANNELS:
        bankDict['channel'+str(channel)] = gpioDict.copy()
    initNodes['bank'+bank] = bankDict


class mcp23017(DeviceBase):
    def init_pre(self):
        self.mcp23017 = self.devisor.runningConnections.open(self.address)
        self.initNodes = initNodes

    def device_thread(self):
        while self.up:
            for address_name in self.mcp23017.both_banks('GPIO'):
                if self.mcp23017.registers[address_name] > 0:
                    changed = self.mcp23017.read_registers(self.mcp23017.both_banks('GPIO'))
                    # use changed to trigger sth.
            time.sleep(self.params['control/refresh-interval'].value)

