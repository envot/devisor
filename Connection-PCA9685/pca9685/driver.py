#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time 

from ..i2cbus.driver import DEVICE_FUNCTION_ARRAY
from ..i2cbus.driver import ConnectionClass as i2cbus

PCA_DICT = {
        'MODE1' : 0x00,
        'MODE2' : 0x01,
        'SUBADR1' : 0x02,
        'SUBADR2' : 0x03,
        'SUBADR3' : 0x04,
        'PRESCALE' : 0xFE,
        'ALL_LED_ON_L' : 0xFA,
        'ALL_LED_ON_H' : 0xFB,
        'ALL_LED_OFF_L' : 0xFC,
        'ALL_LED_OFF_H' : 0xFD,
}
BITS = {
        'RESTART' : 0x80,
        'SLEEP' : 0x10,
        'ALLCALL' : 0x01,
        'INVRT' : 0x10,
        'OUTDRV' : 0x04,
}
CHANNELS = list(range(16))


class ConnectionClass(i2cbus):
    def init_pre(self):
        self.channels = CHANNELS
        self.bits = BITS
        self.registerNames = PCA_DICT
        self.registers = {}
        self.resolution = 2**12

    def init_after(self):
        for channel in self.channels:
            for i,strEnd in enumerate(['_ON_L','_ON_H','_OFF_L','_OFF_H']):
                address = 0x06+4*channel+i
                self.registerNames['LED'+str(channel)+strEnd]=address
                self.deviceFunctions[address] = DEVICE_FUNCTION_ARRAY.copy()
                self.registers[address] = 0
                self.read_register(address)
                time.sleep(0.01)
        self.write(self.registerNames['MODE2'], self.bits['OUTDRV'])
        self.write(self.registerNames['MODE1'], self.bits['ALLCALL'])
        time.sleep(0.01)
        mode1 = self.read(self.registerNames['MODE1'])
        mode1 = mode1 & ~self.bits['SLEEP']
        self.write(self.registerNames['MODE1'], mode1)
        time.sleep(0.01)

    def set_pwm_freq(self, freq_hz):
        currmode = self.read(self.registers[self.registerNames['MODE1']])
        newmode = (currmode & 0x7F) | 0x10
        self.write(self.registerNames['MODE1'], newmode)
        self.write(self.registerNames['PRESCALE'], self._freq2prescale)
        self.write(self.registerNames['MODE1'], currmode)
        time.sleep(0.01)
        self.write(self.registerNames['MODE1'], currmode | 0x80)

    def set_pwm(self, channel, percent, phase=0):
        on, off = self._percent2raw(percent, phase)
        self.set_pwm_raw(channel, on, off)

    def set_pwm_raw(self, channel, on, off):
        if int(channel) in self.channels:
            self.write(self.registerNames['LED'+str(channel)+'_ON_L'], int(on) & 0xFF)
            self.write(self.registerNames['LED'+str(channel)+'_ON_H'], int(on) >> 8)
            self.write(self.registerNames['LED'+str(channel)+'_OFF_L'], int(off) & 0xFF)
            self.write(self.registerNames['LED'+str(channel)+'_OFF_H'], int(off) >> 8)

    def set_all_pwm(self, percent, phase=0):
        on, off = self._percent2raw(percent, phase)
        self.set_all_pwm_raw(self, on, off)

    def set_all_pwm_raw(self, on, off):
        self.write(self.registerNames['ALL_LED_ON_L'], int(on) & 0xFF)
        self.write(self.registerNames['ALL_LED_ON_H'], int(on) >> 8)
        self.write(self.registerNames['ALL_LED_OFF_L'], int(off) & 0xFF)
        self.write(self.registerNames['ALL_LED_OFF_H'], int(off) >> 8)

    def _percent2raw(self, percent, phase):
        phase_raw = phase/100*(self.resolution-1)
        return phase_raw, phase_raw+percent/100*(self.resolution-1)

    def _freq2prescale(self, freq_hz):
        prescaleval = 25e6
        prescaleval /= self.resolution
        prescaleval /= float(freq_hz)
        return round(prescaleval)-1
