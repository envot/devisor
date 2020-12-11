#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
import socket
import sys


class ConnectionClass():
    def __init__(self, devisor, address='device.lan,5555'):
        self.devisor = devisor 
        self.address = address
        addressArray = address.split(',')
        self.hostname = 'device.lan'
        self.port = 5555
        self.TIMEOUT = 0.1 
        self.EOL = '\n'
        if len(addressArray)>0:
            self.hostname = addressArray[0]
        if len(addressArray)==2:
            self.port = int(addressArray[1])
        self.open()
        self.failure = 0

    def write(self, value):
        return self.instr.send(value.encode())

    def ask(self, value):
        self.write(value)
        data = ''
        try:
            while not data.endswith(self.EOL):
                data += self.instr.recv(1024).decode()
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
        self.instr = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.instr.connect((self.hostname,self.port))      
        self.instr.settimeout(self.TIMEOUT)

    def close(self):
        self.instr.close()
        del(self.instr)

    def reonnect(self):
        self.close()
        self.open()
