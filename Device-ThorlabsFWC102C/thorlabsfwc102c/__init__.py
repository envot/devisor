#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@schueppi.com

import time
import sys
from threading import Timer

from devisor.devisorbase import DeviceBase

EOL = '\r'
R2R = '> \n'

control = {}

def process_data(pB, data, cmd):
    if "CMD_NOT_DEFINED" in data:
        pB.new_log('Command failed: '+cmd, 'WARNING')
    dataArray = data.split(EOL)
    indRev = dataArray[::-1].index(cmd)
    ind = len(dataArray)-indRev-1
    return dataArray[ind:][1]

def set_cmd(pB):
    cmd = pB.name+'='+str(pB.value)
    data = pB.dev.instr.ask(cmd)
    if cmd is not data.split(EOL)[0]:
        pB.new_log('Command '+cmd+'failed', 'ERROR')


def get_cmd(pB):
    data = pB.dev.instr.ask(pB.name+'?')
    return process_data(pB, data, pB.name+'?')

def trigger_cmd(pB):
    if pB.value:
        pB.dev.instr.write(pB.name)
        pB.value = False
        pB.publish_value()


control['pos'] = {
    'valueInit' : 1,
    'brokerInit' : False,
    'settable' : True,
    'broker_func': set_cmd,
    'device_func': get_cmd,
}

control['pcount'] = {
    'valueInit' : 1,
    'brokerInit' : False,
    'settable' : True,
    'broker_func': set_cmd,
    'device_func': get_cmd,
}

control['trig'] = {
    'valueInit' : 0,
    'brokerInit' : False,
    'settable' : True,
    'broker_func': set_cmd,
    'device_func': get_cmd,
}

control['speed'] = {
    'valueInit' : 1,
    'brokerInit' : False,
    'settable' : True,
    'broker_func': set_cmd,
    'device_func': get_cmd,
}

control['sensors'] = {
    'valueInit' : 0,
    'brokerInit' : False,
    'settable' : True,
    'broker_func': set_cmd,
    'device_func': get_cmd,
}

control['baud'] = {
    'valueInit' : 1,
    'brokerInit' : False,
    'settable' : True,
    'broker_func': set_cmd,
    'device_func': get_cmd,
}

control['save'] = {
    'valueInit' : False,
    'brokerInit' : False,
    'settable' : True,
    'broker_func': trigger_cmd,
}

def idn_cmd(pB):
    data = pB.dev.instr.ask('*idn?')
    return process_data(pB, data, '*idn?')


control['idn'] = {
    'valueInit' : 'IDN',
    'brokerInit' : False,
    'device_func': idn_cmd,
}

class DeviceClass(DeviceBase):
    def init_pre(self):
        self.instr = self.devisor.runningConnections.open(self.address)
        self.set_eol(EOL)
        self.set_codec()
        self.initNodes = {}
        self.initNodes['control'] = control.copy()

    def set_eol(self, eol=''):
        self.instr.eol = eol

    def set_codec(self, codec='ASCII'):
        self.instr.codec = codec
