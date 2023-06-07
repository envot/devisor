""" DeVisor device to control a Kasli in free-running mode. """
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time
import sys

from devisor.devisorbase import DeviceBase

initNodes = {}
dac = {}
def set_dac_voltage(pB):
    """ Set DAC voltage """
    channel = pB.param.split('/')[-2]
    pB.dev.devisor.kasli.change_dac_volt(int(channel), pB.value)

for i in range(32):
    paramName = str(i)+'/voltage'
    dac[paramName] = {
            'valueInit' : 0.,
            'brokerInit' : True,
            'broker_func' : set_dac_voltage,
            'format' : "-10:10",
            'settable' : True,
            'unit': 'V',
        }

initNodes['dac'] = dac

rf = {}
def set_rf_freq(pB):
    """ Set RF frequency """
    channel = pB.param.split('/')[-2]
    pB.dev.devisor.kasli.set_rf_freq(int(channel), pB.value)
def get_rf_freq(pB):
    """ Set RF frequency """
    channel = pB.param.split('/')[-2]
    return float(pB.dev.devisor.kasli.get_rf_freq(int(channel)))

for i in range(8):
    paramName = str(i)+'/frequency'
    rf[paramName] = {
            'valueInit' : 0.,
            'brokerInit' : True,
            'broker_func' : set_rf_freq,
            'format' : "0:500",
            'settable' : True,
            'unit': 'MHz',
        }

initNodes['rf'] = rf



class DeviceClass(DeviceBase):
    """ Device Class artiqkasli """
    def init_pre(self):
        self.initNodes = initNodes
