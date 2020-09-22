#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time
import random
import math

from devisor.devisorbase import DeviceBase

initNodes = {}

def print_value(pB):
    print('--------------------------- Print Value ---------------------------------')
    print('Greetings from '+pB.dev.name+'.')
    print('Paylod   : '+pB.payload)
    print('Value old: '+str(pB.valueOld))
    print('Value    : '+str(pB.value))

def test_log(pB):
    if pB.value == 'Log Device':
        pB.dev.log.new_log('Test print via enum', 'CRITICAL')
    elif pB.value == 'Log DeVisor':
        pB.dev.devisor.log.new_log('Test print from '+pB.dev.name, 'CRITICAL')
    elif pB.value == 'Print Console':
        print('Test print via enum from '+pB.dev.name+'.')
    pB.device('Choose')


control = {
    'print-value' : {
        'valueInit' : 99.,
        'broker_func' : print_value,
        'brokerInit' : True,
        'settable' : True,
        },
    'test-print-enum' : {
        'broker_func' : test_log,
        'valueInit' : 'Choose',
        'format' : "Choose,Log Device,Log DeVisor,Print Console",
        'datatype' : 'enum',
        'settable' : True,
        },
}
initNodes['control'] = control

randomizer = {}
randomizer['refresh-interval'] = {
    'valueInit' : 5.,
    'brokerInit' : True,
    'format' : "0.1:100",
    'settable' : True,
    'unit': 's',
}
randomizer['random-number'] = {
    'valueInit' : 0.,
    'brokerInit' : False,
}
initNodes['randomizer'] = randomizer

sineWave = {}
sineWave['frequency'] = {
    'valueInit' : 0.1,
    'brokerInit' : True,
    'format' : "1:1000",
    'settable' : True,
    'unit': 'mHz',
}
sineWave['value'] = {
    'valueInit' : 0.,
    'brokerInit' : False,
}
initNodes['sine-wave'] = sineWave


class DeviceClass(DeviceBase):
    def init_pre(self):
        self.initNodes = initNodes
        self.lastSineWave = 0.
        self.lastRandomNumber = 0.

    def device_thread(self):
        while self.up:
            currTime = time.time()
            if self.lastRandomNumber + self.params['randomizer/refresh-interval'].value < currTime:
                self.params['randomizer/random-number'].device(100*random.random())
                self.lastRandomNumber = currTime
            if self.lastSineWave + 1e-2*1e3/(self.params['sine-wave/frequency'].value) < currTime:
                self.params['sine-wave/value'].device(50*(1+math.sin(2.*math.pi*1e-3* self.params['sine-wave/frequency'].value * time.time())))
                self.lastSineWave = currTime
            time.sleep(0.025)
