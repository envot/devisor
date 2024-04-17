#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

from devisor.devisorbase import DeviceBase
import time

from adafruit_servokit import ServoKit    #https://circuitpython.readthedocs.io/projects/servokit/en/latest/

initNodes = {}

def create_servo(pB):
    servoName = pB.dev.params['config/name'].value
    address = pB.dev.params['config/address'].value
    if pB.value:
        if not servoName in pB.dev.params['config/servos'].value:
            pB.dev.create_servo(servoName, address)
        else:
            pB.dev.log.new_log('Servo "'+ servoName + '" already running.')
    pB.publish_value(False)

def handle_servos(pB):
    servos2del = []
    for startedServoName in pB.dev.servos:
        if not startedServoName in pB.value:
            servos2del.append(startedServoName)
    for servo2del in servos2del:
        pB.dev.log.new_log('We close '+servo2del+'.')
        pB.dev.servos[servo2del].exit()
        del(pB.dev.servos[servo2del])
    for servoName in pB.value:
        if not servoName in pB.dev.servos:
            pB.dev.create_servo(servoName, pB.value[servoName])

config = {
    'create': {
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : create_servo,
        'settable' : True,
        },
    'name': {
        'valueInit' : 'servo-name',
        'brokerInit' : True,
        'settable' : True,
        },
    'address': {
        'valueInit' : '1',
        'brokerInit' : True,
        'settable' : True,
        },
    'servos': {
        'valueInit' : {},
        'brokerInit' : True,
        'broker_func' : handle_servos,
        'settable' : True,
        },
}

order = list(config.keys())
order.remove('servos')
order.insert(0, 'servos')
initNodes['config'] = config

def broker_change_value(pB):
    if pB.value:
        pB.dev.servos[pB.name].set_servo(pB.dev.params['servos/'+pB.name+'/value_true'].value)
    else:
        pB.dev.servos[pB.name].set_servo(pB.dev.params['servos/'+pB.name+'/value_false'].value)

servoInitDict = {
    'valueInit' : False,
    'brokerInit' : False,
    'broker_func' : broker_change_value,
    'settable' : True,
}

servoPosInitDict = {
    'valueInit' : 0.,
    'brokerInit' : True,
    'format' : "0:100",
    'settable' : True,
    'unit' : '%',
}

def set_servo_pwm(servo):
    servo.dev.pca.servo[servo.ch].angle = servo.value
    time.sleep(0.1)
    servo.dev.pca.servo[servo.ch].angle = None

class Servo():
    def __init__(self, dev, name, address):
        self.dev = dev
        self.devisor = dev.devisor
        self.name = name
        self.ch = int(address)
        self.set_func = set_servo_pwm
        self.init_params()

    def init_params(self):
        self.dev.create_property(self.name, 'servos', servoInitDict)
        self.dev.create_property(self.name+'/value_false', 'servos', servoPosInitDict)
        self.dev.create_property(self.name+'/value_true', 'servos', servoPosInitDict)
        self.set_servo(0)

    def exit(self):
        self.dev.remove_property(self.name, 'servos')

    def set_servo(self, value):
        self.value = value
        self.set_func(self)

    def set_func(self, dummy):
        pass

class DeviceClass(DeviceBase):
    def init_pre(self):
        self.nbPCAServo=16 
        self.MIN_IMP  =[500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500, 500]
        self.MAX_IMP  =[2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500, 2500]
        self.pca = ServoKit(channels=16)
        for i in range(self.nbPCAServo):
            self.pca.servo[i].set_pulse_width_range(self.MIN_IMP[i] , self.MAX_IMP[i])
        self.servos = {}
        self.initNodes = initNodes
        

    def create_servo(self, name, address):
        if name in self.servos:
            self.devices.log('Servo name "'
                    +name
                    +'" already in running.', 30)
        else:
            self.servos[name] = Servo(self, name, address)
            if 'config/servos' in self.params:
                self.params['config/servos'].value[name] = address
                self.params['config/servos'].publish_value()
