#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

from devisor.devisorbase import DeviceBase

initNodes = {}

def create_led(pB):
    ledName = pB.dev.params['control/name'].value
    address = pB.dev.params['control/address'].value
    if pB.value:
        if not ledName in pB.dev.params['control/leds'].value:
            pB.dev.create_led(ledName, address)
        else:
            pB.dev.log.new_log('LED "'+ ledName + '" already running.')
    pB.device(False)

def handle_leds(pB):
    leds2del = []
    for startedLEDName in pB.dev.leds:
        if not startedLEDName in pB.value:
            leds2del.append(startedLEDName)
    for led2del in leds2del:
        pB.dev.log.new_log('We close '+led2del+'.')
        pB.dev.leds[led2del].exit()
        del(pB.dev.leds[led2del])
    for ledName in pB.value:
        if not ledName in pB.dev.leds:
            pB.dev.create_led(ledName, pB.value[ledName])


control = {
    'create': {
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : create_led,
        'settable' : True,
        },
    'name': {
        'valueInit' : 'led-name',
        'brokerInit' : True,
        'settable' : True,
        },
    'address': {
        'valueInit' : 'pwm,pca9685,1,0x40,0',
        'brokerInit' : True,
        'settable' : True,
        },
    'leds': {
        'valueInit' : {},
        'brokerInit' : True,
        'broker_func' : handle_leds,
        'settable' : True,
        },
}

order = list(control.keys())
order.remove('leds')
order.insert(0, 'leds')
initNodes['control'] = control

def broker_change_value(pB):
    pB.dev.leds[pB.name].set_led(pB.value)

ledInitDict = {
    'valueInit' : 0.,
    'brokerInit' : False,
    'broker_func' : broker_change_value,
    'format' : "0:100",
    'settable' : True,
    'unit' : '%',
}

def set_led_pwm(led):
    led.pwm.set_pwm(led.value)


class LED():
    def __init__(self, dev, name, address):
        self.dev = dev
        self.devisor = dev.devisor
        self.name = name
        addressArray = address.split(',')
        if addressArray[0] == 'pwm':
            self.pwm = self.devisor.runningConnections.open(
                    ','.join(addressArray))
            self.set_func = set_led_pwm
        else:
            return False
        self.init_params()

    def init_params(self):
        self.dev.create_property(self.name, 'leds', ledInitDict)
        if 'leds/'+self.name in self.dev.initBrokerMsgs:
            self.set_led(
                    float(self.dev.initBrokerMsgs['leds/'+self.name]))

    def exit(self):
        self.dev.remove_property(self.name, 'leds')

    def set_led(self, value):
        self.value = value
        self.set_func(self)

    def set_func(self, dummy):
        pass

class DeviceClass(DeviceBase):
    def init_pre(self):
        self.leds = {}
        self.initNodes = initNodes

    def create_led(self, name, address):
        if name in self.leds:
            self.devices.log('LED name "'
                    +name
                    +'" already in running.', 30)
        else:
            self.leds[name] = LED(self, name, address)
            if 'control/leds' in self.params:
                self.params['control/leds'].value[name] = address
                self.params['control/leds'].publish_value()
