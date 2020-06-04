#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time
from threading import Timer

from devisor.devisorbase import DeviceBase

initNodes = {}

def create_motor(pB):
    motorName = pB.dev.params['zcontrol/name'].value
    addresses = pB.dev.params['zcontrol/addresses'].value
    if pB.value:
        if not motorName in pB.dev.params['zcontrol/motors'].value:
            pB.dev.create_motor(motorName, addresses)
        else:
            pB.dev.log.new_log('Motor "'+ motorName + '" already running.')
    pB.device(False)

def handle_motors(pB):
    motors2del = []
    for startedMotorName in pB.dev.motors:
        if not startedMotorName in pB.value:
            motors2del.append(startedMotorName)
    for motor2del in motors2del:
        pB.dev.log.new_log('We close '+motor2del+'.')
        pB.dev.motors[motor2del].exit()
        del(pB.dev.motors[motor2del])
    for motorName in pB.value:
        if not motorName in pB.dev.motors:
            pB.dev.create_motor(motorName, pB.value[motorName])


zcontrol = {
    'create': {
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : create_motor,
        'settable' : True,
        },
    'name': {
        'valueInit' : 'motor-name',
        'brokerInit' : True,
        'settable' : True,
        },
    'addresses': {
        'valueInit' : 'gpio,mcp23017,1,0x20,A0,out:gpio,mcp23017,1,0x20,B0,out',
        'brokerInit' : True,
        'settable' : True,
        },
    'motors': {
        'valueInit' : {},
        'brokerInit' : True,
        'broker_func' : handle_motors,
        'settable' : True,
        },
}

order = list(zcontrol.keys())
order.remove('motors')
order.insert(0, 'motors')
initNodes['zcontrol'] = zcontrol

def broker_change_pos(pB):
    pB.dev.motors[pB.name].change_pos(pB.value)
motorInitDict = {
    'valueInit' : 0.,
    'brokerInit' : False,
    'broker_func' : broker_change_pos,
    'format' : "0:100",
    'settable' : True,
    'unit' : '%',
}

DEFAULT_TIME = 5.

def broker_motor_time(pB):
    pB.dev.motors[pB.name].change_motor_time(pB.value)
timeInitDict = {
    'valueInit' : DEFAULT_TIME,
    'brokerInit' : False,
    'broker_func' : broker_motor_time,
    'settable' : True,
    'unit' : 's',
}

class Motor():
    def __init__(self, dev, name, addresses):
        self.dev = dev
        self.devisor = dev.devisor
        self.name = name
        addressesArray = addresses.split(':')
        self.gpios = []
        for address in addressesArray:
            addressArray = address.split(',')
            self.gpios.append(self.devisor.runningConnections.open(
                                ','.join(addressArray)))
        self.pos = 0.
        self.xE = 100.
        self.sT = 1.
        self.startTime = time.time()
        self.StopThread = Timer(0, self.stop_motor)
        self.init_params()

    def init_params(self):
        self.dev.create_property(self.name, 'motors', motorInitDict)
        self.dev.create_property(self.name, 'times', timeInitDict)
        if 'motors/'+self.name in self.dev.initBrokerMsgs:
            self.change_motor_time(float(self.dev.initBrokerMsgs['times/'+self.name]))
            self.dev.params['times/'+self.name].device(self.tT)
            self.pos = float(self.dev.initBrokerMsgs['motors/'+self.name])
            self.dev.params['motors/'+self.name].device(self.pos)
        else:
            self.tT = DEFAULT_TIME
        self.update_params()

    def exit(self):
        self.dev.remove_property(self.name, 'motors')
        self.dev.remove_property(self.name, 'times')

    def change_motor_time(self, totalTime):
        self.tT = totalTime 
        self.update_params()

    def change_soft_start_time(self, softStartTime):
        self.sT = softStartTime
        self.update_params()

    def change_pos(self, posNew):
        if self.StopThread.isAlive():
            oldPos = self.curr_pos()
        else:
            oldPos = self.pos
        distance = posNew - self.pos
        moveTime = self.move_time(abs(distance))
        indexNew = self._get_index(distance)
        if self.StopThread.isAlive():
            self.StopThread.cancel()
            if self.runningIndex == indexNew:
                self.start_thread(moveTime)
            else:
                self.gpios[self.runningIndex].write(False)
                self.start_motor(indexNew, moveTime)
        else:
            self.start_motor(indexNew, moveTime)

    def start_motor(self, index, moveTime):
        self.runningIndex = index
        self.startTime = time.time()
        self.gpios[self.runningIndex].write(True)
        self.start_thread(moveTime)

    def start_thread(self, moveTime):
        self.StopThread = Timer(moveTime, self.stop_motor)
        self.StopThread.start()

    def stop_motor(self):
        self.gpios[self.runningIndex].write(False)
        self.pos = self.dev.params['motors/'+self.name].value

    def _get_index(self, distance):
        if distance < 0:
            return 0
        else:
            return 1

    def update_params(self):
        self.v_0()
        self.a_0()
        self.x_s()
    
    def x_s(self):
        self.xS = self.xE * (1 - (self.tT - self.sT)/(self.tT - 0.5*self.sT))
    
    def v_0(self):
        self.v0 = self.xE / (self.tT-0.5*self.sT)
    
    def a_0(self):
        self.a0 = self.v0/self.sT

    def move_time(self, x):
        if x == 0:
            return 0
        if x < self.xS:
            return (2*x/self.a0)**0.5
        else:
            return (x-self.xS)/self.v0 + self.sT

    def curr_pos(self):
        timeDiff = time.time() - self.startTime
        if timeDiff == 0:
            return 0
        if timeDiff < self.sT:
            return 0.5*self.a0*timeDiff**2
        else:
            return self.v0*(timeDiff-self.sT) + self.xS


class motortimers(DeviceBase):
    def init_pre(self):
        self.motors = {}
        self.initNodes = initNodes

    def create_motor(self, name, addresses):
        if name in self.motors:
            self.devices.log('Motor name "'
                    +name
                    +'" already in running.', 30)
        else:
            self.motors[name] = Motor(self, name, addresses)
            if 'zcontrol/motors' in self.params:
                self.params['zcontrol/motors'].value[name] = addresses
                self.params['zcontrol/motors'].publish_value()
