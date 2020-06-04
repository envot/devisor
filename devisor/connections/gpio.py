#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

def mcp_write(gpio):
    value = gpio.value
    return gpio.con.write_bit('GPIO'+gpio.bank,
                    gpio.channel,
                    value)

def mcp_read(gpio):
    return gpio.con.read_bit('GPIO'+gpio.bank,
                    gpio.channel)

def rpi_read(gpio):
    return gpio.GPIO.input(gpio.channel)

def rpi_write(gpio):
    state = gpio.value
    if state:
        state = gpio.GPIO.HIGH
    else:
        state = gpio.GPIO.LOW
    return gpio.GPIO.output(gpio.channel, state)

class gpio():
    def __init__(self, devisor, address='mcp23017,1,0x20,A0,out'):
        self.devisor = devisor 
        addressArray = address.split(',')
        if addressArray[-1].lower() in ['out','true']:
            self.out = True
        elif addressArray[-1].lower() in ['in','false']:
            self.out = False
        else:
            self.out = bool(int(addressArray[-1]))
        if addressArray[0] == 'rpi':
            self.init_rpi(addressArray)
        elif addressArray[0] == 'mcp23017':
            self.init_mcp23017(addressArray)

    def init_rpi(self, addressArray):
        self.channel = addressArray[1]
        import RPi.GPIO as GPIO
        self.GPIO = GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        if self.out:
            gpioType = self.GPIO.OUT
            self.write_func = rpi_write
        else:
            gpioType = self.GPIO.IN
            self.read_func = rpi_read
        self.GPIO.setup(channel, gpioType)

    def init_mcp23017(self, addressArray):
        self.bank = addressArray[3][0]
        self.channel = int(addressArray[3][1])
        self.con = self.devisor.runningConnections.open(
                ','.join(addressArray[:-2]))
        self.con.write_bit('IODIR'+self.bank,
                self.channel,
                (not self.out))
        self.read_func = mcp_read
        if self.out:
            self.write_func = mcp_write

    def write(self, value):
        self.value = value
        return self.write_func(self)

    def write_func(self, dummy):
        pass

    def read(self):
        self.read_func(self)

    def read_func(self, dummy):
        pass
