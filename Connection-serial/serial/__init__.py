#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
import serial
import sys

class ConnectionClass():
    def __init__(self, devisor, address='/dev/ttyUSB0'):
        self.devisor = devisor
        self.address = address
        self.addressArray = address.split(',')
        self.eol = '\r\n'
        self.codec = 'ASCII'
        self.open()

    def write(self, value, codec=True):
        if not type(codec)==str:
            if codec:
                codec = self.codec
            else:
                codec = ''
        return self.instr.write((value+self.eol).encode(self.codec))

    def read(self, length=1024, codec=True):
        dataRaw = self.instr.read(length)
        if type(codec)==str:
            return self.decode(dataRaw, codec)
        elif codec:
            return self.decode(dataRaw, self.codec)
        else:
            return dataRaw

    def decode(self, dataRaw, codec):
        try:
            data = dataRaw.decode(codec)
        except Exception:
            err = sys.exc_info()[1]
            self.devisor.log.new_log('Received data could not be decoeded with codec: '
                    +str(codec)+' due to: '+str(err), "WARNING")
            data = dataRaw
        return data


    def open(self):
        self.instr = serial.Serial(self.addressArray[0],
                baudrate = 115200, bytesize=8, parity=serial.PARITY_NONE,
                stopbits=1, xonxoff=0, rtscts=0, timeout=0.1)
        self.devisor.log.new_log('Connection "serial" successfully connect to "'
                    +self.addressArray[0]+'"', "INFO")

    def close(self):
        self.instr.close()
        del(self.instr)

    def reonnect(self):
        self.close()
        self.open()
