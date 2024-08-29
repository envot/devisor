#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time
import sys
from threading import Timer

from devisor.devisorbase import DeviceBase

EOL = '\r\n'
R2R = '> '

control = {}

def process_data(data, cmd, returnInd=1):
    if "CMD_NOT_DEFINED" in data:
        pB.new_log('Command failed: '+cmd, 'WARNING')
    dataArray = data.split(EOL)
    indRev = dataArray[::-1].index(cmd)
    ind = len(dataArray)-indRev-1
    return dataArray[ind:][returnInd]

def set_cmd(pB):
    cmd = pB.name+'='+str(pB.value)
    data = pB.dev.instr.ask(cmd)
    if cmd is not data.split(EOL)[0]:
        pB.new_log('Command '+cmd+'failed', 'ERROR')


def get_cmd(pB):
    data = pB.dev.instr.ask('sh '+pB.name)
    return process_data(data, 'sh '+pB.name)

def get_info(pB):
    data = pB.dev.instr.ask(pB.name)
    return process_data(data, pB.name)

def trigger_cmd(pB):
    if pB.value:
        pB.dev.instr.write(pB.name)
        pB.value = False
        pB.publish_value()


control['serial'] = {
    'valueInit' : '',
    'brokerInit' : False,
    'device_func': get_cmd,
}

control['error'] = {
    'valueInit' : '',
    'brokerInit' : False,
    'device_func': get_info,
}

control['version'] = {
    'valueInit' : '',
    'brokerInit' : False,
    'device_func': get_info,
}

def get_temp_ld(pB):
    data = pB.dev.instr.ask('sh temp')
    rawdata = process_data(data, 'sh temp')
    return float(rawdata[len('TEMP = '):rawdata.find(' C')])

control['temperature/laserdiode'] = {
    'valueInit' : 0.,
    'brokerInit' : False,
    'device_func': get_temp_ld,
    'unit': 'deg C',
}

def get_temp_sys(pB):
    data = pB.dev.instr.ask('sh temp sys')
    rawdata = process_data(data, 'sh temp sys')
    return float(rawdata[len('TEMP = '):rawdata.find(' C')])
control['temperature/system'] = {
    'valueInit' : 0.,
    'brokerInit' : False,
    'device_func': get_temp_sys,
    'unit': 'deg C',
}

def get_powerup(pB):
    data = pB.dev.instr.ask('sh tim')
    rawdata = process_data(data, 'sh tim')
    return int(rawdata[len('PowerUP: '):rawdata.find(' s')])

control['uptime/power'] = {
    'valueInit' : 0,
    'brokerInit' : False,
    'device_func': get_powerup,
    'unit': 's',
}

def get_laserup(pB):
    data = pB.dev.instr.ask('sh tim')
    rawdata = process_data(data, 'sh tim', returnInd=2)
    return int(rawdata[len('LaserUP: '):rawdata.find(' s')])
control['uptime/laser'] = {
    'valueInit' : 0,
    'brokerInit' : False,
    'device_func': get_laserup,
    'unit': 's',
}


def get_laserstatus(pB):
    data = pB.dev.instr.ask('sta la')
    rawdata = process_data(data, 'sta la')
    if rawdata == 'ON':
        return True
    else:
        return False

def set_laserstatus(pB):
    if pB.value:
        cmd = 'la on'
    else:
        cmd = 'la off'
    data = pB.dev.instr.ask(cmd)
    if cmd is not data.split(EOL)[0]:
        pB.new_log('Command '+cmd+'failed', 'ERROR')

control['laser'] = {
    'valueInit' : False,
    'brokerInit' : False,
    'device_func': get_laserstatus,
    'broker_func': set_laserstatus,
}

def set_ch1pow(pB):
    cmd = 'ch 1 pow '+str(pB.value)
    data = pB.dev.instr.ask(cmd)
    if cmd is not data.split(EOL)[0]:
        pB.new_log('Command '+cmd+'failed', 'ERROR')
control['channel1-power'] = {
    'valueInit' : 0.,
    'brokerInit' : True,
    'broker_func': set_ch1pow,
    'unit': 'mW',
}


class DeviceClass(DeviceBase):
    def init_pre(self):
        self.instr = self.devisor.runningConnections.open(self.address)
        self.set_eol(EOL)
        self.set_r2r(R2R)
        self.set_codec()
        self.instr.write('echo on')
        print(self.instr.read())
        self.initNodes = {}
        self.initNodes['control'] = control.copy()

    def set_eol(self, eol=''):
        self.instr.eol = eol

    def set_r2r(self, r2r=''):
        self.instr.r2r =r2r 

    def set_codec(self, codec='ASCII'):
        self.instr.codec = codec
