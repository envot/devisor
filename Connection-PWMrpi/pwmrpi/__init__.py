#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

def pca_set(pwm):
    value = pwm.value
    if pwm.channel % 2 == 0:
        return pwm.con.set_pwm_raw(pwm.channel, 0, value)
    else:
        return pwm.con.set_pwm_raw(pwm.channel, 4095-value, 4095)

def rpi_write(pwm):
    value = pwm.value
    pwm.pwm.ChangeDutyCycle(value)

class ConnectionClass():
    def __init__(self, devisor, address='pca9685,1,0x40,0'):
        self.devisor = devisor 
        addressArray = address.split(',')
        if addressArray[0] == 'rpi':
            self.init_rpi(addressArray)
        elif addressArray[0] == 'pca9685':
            self.init_pca9586(addressArray)

    def init_rpi(self, addressArray):
        self.channel = addressArray[1]
        import RPi.GPIO as GPIO
        self.GPIO = GPIO
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(channel, self.GPIO.OUT)
        self.pwm = GPIO.PWM(channel, 0)
        self.resolution = 8
        self.intnumber = 77

    def init_pca9586(self, addressArray):
        self.channel = int(addressArray[3])
        self.con = self.devisor.runningConnections.open(
                ','.join(addressArray[:-1]))
        self.set_func = pca_set
        self.resolution = 12
        self.intnumber = 47

    def set_pwm(self, value):
        self.value = self._convert_value(value)
        return self.set_func(self)

    def set_func(self, dummy):
        pass

    def _convert_value(self, value):
        if value < self.intnumber:
            return value
        else:
            return int(2**(self.resolution*value/100)-1)
