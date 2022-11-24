#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
import socket


class ConnectionClass():
    def __init__(self, devisor, address='device.lan:5555'):
        self.devisor = devisor 
        self.address = address
        addressArray = address.split(':')
        self.hostname = 'device.lan'
        self.port = 5555
        self.TIMEOUT = 1
        if not addressArray[0]=='':
            self.hostname = addressArray[0]
        if len(addressArray)==2:
            self.port = int(addressArray[1])
        self.open()

    def write(self, value, codec=True):
        if type(codec)==str:
            value = value.encode(codec)
        elif codec:
            value = value.encode()
        self.instr.send(value)

    def read(self, length=1024, codec=True):
        result = self.instr.recv(length)
        if type(codec)==str:
            result = result.decode(codec)
        elif codec:
            result = result.decode()
        if result == None:
            self.devisor.log.new_log('TCP socket: Reading not working',
                    'WARNING')
        return result

    def set_timeout(self, timeoutTime):
        self.instr.settimeout(timeoutTime)

    def open(self):
        self.instr = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.devisor.log.new_log('Connecting to '+self.hostname+' via port '
                +str(self.port)+' established.', 'INFO')
        self.instr.connect((self.hostname,self.port))      
        self.devisor.log.new_log('Connection established.', 'INFO')
        self.instr.settimeout(self.TIMEOUT)

    def close(self):
        self.instr.close()
        del(self.instr)

    def reconnect(self):
        self.close()
        self.open()
