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
        self.addressArray = ['dev/ttyUSB0', '115200', '8', '1', '0.1']
        for i,addressElement in enumerate(address.split(',')):
            self.addressArray[i] = addressElement
        self.eol = '\r\n'
        self.codec = 'ASCII'
        self.instr = self.open()

    def write(self, value, codec=True):
        if not type(codec)==str:
            if codec:
                codec = self.codec
            else:
                return self.instr.write(value)
        return self.instr.write((value+self.eol).encode(codec))

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
            self.devisor.log.new_log('Received data could not be decoded with codec: '
                    +str(codec)+' due to: '+str(err), "WARNING")
            data = dataRaw
        return data


    def open(self):
        try:
            instr = serial.Serial(self.addressArray[0],
                baudrate=int(self.addressArray[1]),
                bytesize=int(self.addressArray[2]),
                parity=serial.PARITY_NONE,
                stopbits=int(self.addressArray[3]),
                xonxoff=0,
                rtscts=0,
                timeout=float(self.addressArray[4]))
            self.devisor.log.new_log(f'Connection "serial" successfully connected to "{self.addressArray[0]}".', "INFO")
        except:
            instr = None
            self.devisor.log.new_log(f'Connection "serial" to "{self.addressArray[0]}" failed.', "WARNING")
        return instr

    def close(self):
        self.instr.close()
        del(self.instr)

    def reconnect(self):
        self.close()
        self.open()
