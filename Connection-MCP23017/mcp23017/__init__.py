#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

from ...devisorbase import devisor_import
i2cbus = devisor_import('dev', 'i2cbus', 'connection')

MCP_DICT = {
        'IODIRA' : 0x00, # IODIR: I/O DIRECTION REGISTER
        'IODIRB' : 0x01,
        'IPOLA' : 0x02, # IPOL: INPUT POLARITY PORT REGISTER
        'IPOLB' : 0x03,
        'GPINTENA' : 0x04, # GPINTEN: INTERRUPT-ON-CHANGE PINS
        'GPINTENB' : 0x05,
        'DEFVALA' : 0x06, # DEFVAL: DEFAULT VALUE REGISTER
        'DEFVALB' : 0x07,
        'INTCONA' : 0x08, # INTCON: INTERRUPT-ON-CHANGE CONTROL REGISTER
        'INTCONB' : 0x09,
        'IOCON' : 0x0A, # IOCON: I/O EXPANDER CONFIGURATION REGISTER 
        #'IOCON' : 0x0B,
        'GPPUA' : 0x0C, # GPPU: GPIO PULL-UP RESISTOR REGISTER 
        'GPPUB' : 0x0D,
        'INTFA' : 0x0E, # INTF: INTERRUPT FLAG REGISTER 
        'INTFB' : 0x0F,
        'INTCAPA' : 0x10, # INTCAP: INTERRUPT CAPTURED VALUE FOR PORT REGISTER
        'INTCAPB' : 0x11,
        'GPIOA' : 0x12, # GPIO: GENERAL PURPOSE I/O PORT REGISTER 
        'GPIOB' : 0x13,
        'OLATA' : 0x14, # OLAT: OUTPUT LATCH REGISTER 0
        'OLATB' : 0x15,
        }
BANKS = ['A', 'B']
CHANNELS = list(range(8))


class ConnectionClass(i2cbus.ConnectionClass):
    def init_pre(self):
        self.banks = BANKS
        self.registerNames = MCP_DICT
        self.registers = {}

    def both_banks(self, address_name):
        addresses = []
        for i,letter in enumerate(self.banks):
            addresses.append(self.registerNames[address_name+letter])
        return addresses
