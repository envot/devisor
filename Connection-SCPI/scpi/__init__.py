#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
import time
import sys

class ConnectionClass():
    def __init__(self, devisor, address='usbtmc,0x699,0x03a2'):
        self.devisor = devisor 
        self.address = address
        self.con = self.devisor.runningConnections.open(address)
        self.block = False
        self.eol = '\n'
        self.codec = True
        self.failure = 0
        #self.read_empty()

    def write(self, value, codec=True):
        self._wait_ready()
        self._write_raw(value, codec)
        self.block = False

    def _write_raw(self, value, codec=True):
        try:
            self.con.write(value+self.eol, codec=codec)
        except:
            self.devisor.log.new_log('Connection "scpi" failed to write "'
                +value+'".', "ERROR")

    def read(self, length=1024):
        self._wait_ready()
        try:
            result = self.con.read(length=length, codec=self.codec)
            self.block = False
            return result
        except:
            self.block = False
            self.devisor.log.new_log('Connection "scpi" failed to read.',
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
            self.devisor.log.new_log('Connection "scpi" read empty: '
                    +str(read_string), "INFO")

    def ask(self, value):
        self._wait_ready()
        self._write_raw(value)
        data = ''
        try:
            while not data.endswith(self.eol):
                data += self.con.read(1024, codec=self.codec)
            self.failure = 0
            self.block = False
            return data[:-len(self.eol)]
        except Exception:
            err = sys.exc_info()[1]
            self.failure += 1
            if self.failure < 2:
                self.devisor.log.new_log('Connection "scpi" failed to ask for "'
                    +value+'":'+str(err), "WARNING")
                self.block = False
                data = self.ask(value)
            elif self.failure < 3:
                self.devisor.log.new_log('Connection "scpi" failed again to ask for "'
                    +value+'":'+str(err)+"... now reconnect TCP socket.", "WARNING")
                self.con.reconnect()
                self.block = False
                data = self.ask(value)
            else:
                self.devisor.log.new_log('Connection "scpi" failed after reconnect to ask for "'
                    +value+'":'+str(err)+"... return empty String.", "ERROR")
                self.failure = 0
            self.block = False
            return ''

    def _wait_ready(self):
        while self.block:
            time.sleep(0.01)
        self.block = True

    def set_timeout(self, timeoutTime):
        self.instr.set_timeout(timeoutTime)

