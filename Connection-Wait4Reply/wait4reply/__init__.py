#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
import time
import sys

class ConnectionClass():
    def __init__(self, devisor, address='serial,/dev/ttyUSB0'):
        self.devisor = devisor 
        self.address = address
        self.con = self.devisor.runningConnections.open(address)
        self.con.eol = ''
        self.block = False
        self.eol = '\r'
        self.r2r = '> '
        self.codec = True
        self.failure = 0
        self.maxTries = 10
        #self.read_empty()

    def write(self, value, codec=True):
        self._wait_ready()
        self._write_raw(value, codec)
        self.block = False

    def _write_raw(self, value, codec=True):
        try:
            self.con.write(value+self.eol, codec=codec)
        except:
            self.devisor.log.new_log('Connection "wait4reply" failed to write "'
                +value+'".', "ERROR")

    def read(self, length=1024):
        self._wait_ready()
        try:
            result = self.con.read(length=length, codec=self.codec)
            self.block = False
            return result
        except:
            self.block = False
            self.devisor.log.new_log('Connection "wait4reply" failed to read.',
                    "ERROR")

    def read_empty(self):
        result = 'Start'
        read_string = ''
        while len(result) > 0:
            result = self.read()
            if result == None:
                return True
            read_string += result
        if len(read_string) > 0:
            self.devisor.log.new_log('Connection "wait4reply" read empty: '
                    +str(read_string), "INFO")

    def ask(self, value):
        self._wait_ready()
        self._write_raw(value)
        data = ''
        while not data.endswith(self.r2r) and self.failure < self.maxTries:
            data += self.con.read(1024, codec=self.codec)
            time.sleep(0.1)
            self.failure += 1
        self.failure = 0
        self.block = False
        return data[:-len(self.r2r)]

    def _wait_ready(self):
        while self.block:
            time.sleep(0.01)
        self.block = True

    def set_timeout(self, timeoutTime):
        self.con.set_timeout(timeoutTime)
