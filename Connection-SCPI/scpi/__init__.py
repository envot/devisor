#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
import time

class ConnectionClass():
    def __init__(self, devisor, address='usbtmc,0x699,0x03a2'):
        self.devisor = devisor 
        self.address = address
        self.con = self.devisor.runningConnections.open(address)
        self.read_empty()
        self.block = False

    def write(self, value, encode=True):
        self._wait_ready()
        try:
            self.con.write(value)
        except:
            self.devisor.log.new_log('Connection "scpi" failed to write "'
                +value+'".', "ERROR")
        self.block = False

    def read(self, length=1024, codec=True):
        self._wait_ready()
        try:
            self.con.read(length=length, codec=codec)
        except:
            self.devisor.log.new_log('Connection "scpi" failed to read.', "ERROR")
        self.block = False

    def read_empty(self):
        result = 'Start'
        read_string = ''
        while len(result) > 0:
            result = self.read()
            read_string += result
        if len(read_string) > 0:
            self.devisor.log.new_log('Connection "scpi" read empty: '+str(read_string), "ERROR")

    def ask(self, value):
        self._wait_ready()
        try:
            reply = self.con.ask(value)
        except:
            self.devisor.log.new_log('Connection "scpi" failed to ask for "'
                +value+'".', "ERROR")
            reply = ''
        self.block = False
        return reply

    def _wait_ready(self):
        while self.block:
            time.sleep(0.01)
        self.block = True
