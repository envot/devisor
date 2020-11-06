#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import sys
import time
from threading import Timer

from devisor.devisorbase import DeviceBase

initNodes = {}

def create_digout(pB):
    digoutName = pB.dev.params['config/name'].value
    address = pB.dev.params['config/address'].value
    if pB.value:
        if not digoutName in pB.dev.params['config/digouts'].value:
            pB.dev.create_digout(digoutName, address)
        else:
            pB.dev.log.new_log('DigOut "'+ digoutName + '" already running.')
    pB.device(False)

def handle_digouts(pB):
    digouts2del = []
    for startedDigiOutName in pB.dev.digouts:
        if not startedDigiOutName in pB.value:
            digouts2del.append(startedDigiOutName)
    for digout2del in digouts2del:
        pB.dev.log.new_log('We close '+digout2del+'.')
        pB.dev.digouts[digout2del].exit()
        del(pB.dev.digouts[digout2del])
    for digoutName in pB.value:
        if not digoutName in pB.dev.digouts:
            pB.dev.create_digout(digoutName, pB.value[digoutName])


config = {
    'create': {
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : create_digout,
        'settable' : True,
        },
    'name': {
        'valueInit' : 'digout-name',
        'brokerInit' : True,
        'settable' : True,
        },
    'address': {
        'valueInit' : 'digout,rpi,2',
        'brokerInit' : True,
        'settable' : True,
        },
    'digouts': {
        'valueInit' : {},
        'brokerInit' : True,
        'broker_func' : handle_digouts,
        'settable' : True,
        },
}

order = list(config.keys())
order.remove('digouts')
order.insert(0, 'digouts')
initNodes['config'] = config

def broker_trigger(pB):
    pB.dev.digouts[pB.name].trigger()
digoutInitDict = {
    'valueInit' : False,
    'brokerInit' : False,
    'broker_func' : broker_trigger,
    'settable' : True,
}

DEFAULT_TIME = 0.

def broker_digout_time(pB):
    pB.dev.digouts[pB.name].change_digout_time(pB.value)
timeInitDict = {
    'valueInit' : DEFAULT_TIME,
    'brokerInit' : False,
    'broker_func' : broker_digout_time,
    'settable' : True,
    'unit' : 's',
}

class DigOut():
    def __init__(self, dev, name, address):
        self.dev = dev
        self.devisor = dev.devisor
        self.name = name
        self.digout = self.devisor.runningConnections.open(address)
        self.tT = DEFAULT_TIME
        self.startTime = time.time()
        self.StopThread = Timer(0, self.trigger_output)
        self.init_params()

    def init_params(self):
        self.dev.create_property(self.name, 'digouts', digoutInitDict)
        self.dev.create_property(self.name, 'triggertimes', timeInitDict)
        if 'digouts/'+self.name in self.dev.initBrokerMsgs:
            self.change_digout_time(float(self.dev.initBrokerMsgs['triggertimes/'+self.name]))
            self.dev.params['triggertimes/'+self.name].device(self.tT)
            self.write_output(bool(self.dev.initBrokerMsgs['digouts/'+self.name]))
            self.dev.params['digouts/'+self.name].device(self.output)
        else:
            self.write_output(False)

    def exit(self):
        self.dev.remove_property(self.name, 'digouts')
        self.dev.remove_property(self.name, 'triggertimes')

    def change_digout_time(self, triggerTime):
        if self.StopThread.isAlive():
            self.StopThread.cancel()
            if triggerTime > self.tT:
                self.start_thread(self.triggerTime-self.tT)
            if triggerTime < self.tT:
                if self.startTime+triggerTime > time.time():
                    self.start_thread(self.triggerTime-self.tT)
                else:
                    self.trigger_output()
        self.dev.log.new_log('Changed Trigger Time"'+ self.name 
                + '" from  '+str(self.tT)
                + '" to '+str(triggerTime)+'.', 'DEBUG')
        self.tT = triggerTime 

    def trigger(self):
        if self.StopThread.isAlive():
            self.StopThread.cancel()
            self.trigger_output()
        if self.tT:
            self.start_trigger()
        else:
            self.trigger_output()

    def start_trigger(self):
        self.startTime = time.time()
        self.trigger_output()
        self.start_thread(self.tT)

    def start_thread(self, triggerTime):
        self.StopThread = Timer(triggerTime, self.trigger_output)
        self.StopThread.start()

    def trigger_output(self):
        if self.output:
            self.write_output(False)
        else:
            self.write_output(True)

    def write_output(self, value):
        self.digout.write(value)
        self.dev.params['digouts/'+self.name].device(value)
        self.dev.log.new_log('Set DigOut "'+ self.name + '" to '+str(value)+'.', 'DEBUG')
        self.output = value

class DeviceClass(DeviceBase):
    def init_pre(self):
        self.digouts = {}
        self.initNodes = initNodes

    def create_digout(self, name, address):
        if name in self.digouts:
            self.devices.log('DigOut name "'
                    +name
                    +'" already in running.', 30)
        else:
            self.digouts[name] = DigOut(self, name, address)
            if 'config/digouts' in self.params:
                self.params['config/digouts'].value[name] = address
                self.params['config/digouts'].publish_value()
