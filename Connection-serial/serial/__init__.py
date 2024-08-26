#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
import serial
import sys

class ConnectionClass():
    def __init__(self, devisor, address='/dev/ttyUSB0', baudrate=115200, bytesize=8, parity="none", stopbits=1):
        self.devisor = devisor
        self.address = address
        self.addressArray = address.split(',')
        self.eol = '\r\n'
        self.codec = 'ASCII'

        # Connection params
        self.parity_dict = {"none":serial.PARITY_NONE, "even":serial.PARITY_EVEN, "odd":serial.PARITY_ODD, "mark":serial.PARITY_MARK, "space":serial.PARITY_SPACE}
        self.stopbits_dict = {1:serial.STOPBITS_ONE, 1.5:serial.STOPBITS_ONE_POINT_FIVE, 2:serial.STOPBITS_TWO}

        self.baudrate = baudrate if baudrate in [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200] else 115200
        self.bytesize = bytesize if bytesize in [5,6,7,8] else 8
        self.parity = self.parity_dict[parity] if parity in self.parity_dict.keys() else serial.PARITY_NONE
        self.stopbits = self.stopbits_dict[stopbits] if stopbits in self.stopbits_dict.keys() else serial.STOPBITS_ONE

        # Open
        self.instr = self.open()

    def write(self, value, codec=True):
        if not type(codec)==str:
            if codec:
                codec = self.codec
            else:
                return self.instr.write(value)
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
            self.devisor.log.new_log('Received data could not be decoded with codec: '
                    +str(codec)+' due to: '+str(err), "WARNING")
            data = dataRaw
        return data


    def open(self):
        try:
            instr = serial.Serial(self.addressArray[0],
                    baudrate=self.baudrate, bytesize=self.bytesize, parity=self.parity,
                    stopbits=self.stopbits, xonxoff=0, rtscts=0, timeout=0.1)
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
