#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

class ConnectionClass():
    def __init__(self, devisor, address='1'):
        self.devisor = devisor 
        self.channel = int(address)
        import RPi.GPIO as GPIO
        self.GPIO = GPIO
        self.GPIO.setwarnings(False)
        self.GPIO.setmode(self.GPIO.BCM)
        self.GPIO.setup(self.channel, GPIO.OUT)

    def read(self):
        return self.GPIO.input(self.channel)
    
    def write(self, state):
        if state:
            state = self.GPIO.HIGH
        else:
            state = self.GPIO.LOW
        return self.GPIO.output(self.channel, state)
