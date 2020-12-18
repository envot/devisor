#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
import serial 
import sys

class ConnectionClass():
    def __init__(self, devisor, address='/dev/ttyUSB0'):
        self.devsor = devisor 
        self.address = address
        self.addressArray = address.split(',')
        self.EOL = '\r\n'
        self.codec = 'ASCII'
        self.maxTries = 10
        self.open()

    def write(self, value):
        return self.instr.write((value+self.EOL).encode(self.codec))

    def read(self, length=1024, codec=True):
        if type(codec)==str:
            return self.instr.recv(length).decode(codec)
        elif codec:
            return self.instr.recv(length).decode(self.codec)
        else:
            return self.instr.recv(length)


    def ask(self, value):
        self.write(value)
        data = ''
        try:
            tries = 0
            while not data.endswith(self.EOL) and tries<self.maxTries:
                tries += 1
                data += self.instr.read(1024).decode(self.codec)
            self.failure = 0
            return data[:-len(self.EOL)]
        except Exception:
            err = sys.exc_info()[1]
            self.failure += 1
            if self.failure < 2:
                self.devisor.log.new_log('Connection "socket" failed to ask for "'
                    +value+'":'+str(err), "WARNING")
                data = self.ask(value)
            elif self.failure < 3:
                self.devisor.log.new_log('Connection "socket" failed again to ask for "'
                    +value+'":'+str(err)+"... now reconnect socket.", "WARNING")
                self.reconnect()
                data = self.ask(value)
            else:
                self.devisor.log.new_log('Connection "socket" failed after reconnect to ask for "'
                    +value+'":'+str(err)+"... return empty String.", "ERROR")
            return data 

    def open(self):
        self.instr = serial.Serial(self.addressArray[0])
        self.instr.timeout = 0.3

    def close(self):
        self.instr.close()
        del(self.instr)

    def reonnect(self):
        self.close()
        self.open()
