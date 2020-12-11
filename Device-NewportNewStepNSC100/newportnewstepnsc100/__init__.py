#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time

from devisor.devisorbase import devisor_import

scpiPackage = devisor_import(None, 'scpi', 'device')

scpiDict = {
    'AC' : {
        'valueInit' : 0.,
        'format' : '0:624',
        'unit' : "steps/s^2",
    },
    'AU' : {
        'valueInit' : 0.,
        'format' : '0:1239',
        'unit' : "steps/s^2",
    },
    'BA' : {
        'valueInit' : 0,
        'format' : '0:512',
        'unit' : "microsteps",
    },
    'BZ' : {
        'valueInit' : False,
        'readable' : False,
    },
    # gives back: b'1JA? 00.00\x00\x00\x00\x00\r\n'
    #'JA' : {
    #    'valueInit' : 0,
    #    'format' : '-8:8',
    #},
    # don't know why not working
    #'JS' : {
    #    'valueInit' : 0,
    #    'format' : '0:255',
    #},
    'MF' : {
        'valueInit' : False,
        'readable' : False,
    },
    'MO' : {
        'valueInit' : False,
        'readable' : False,
    },
    'OR' : {
        'valueInit' : False,
        'readable' : False,
    },
    'PA' : {
        'valueInit' : 0,
        'format' : '-60000:120000',
        'unit' : "mircosteps",
    },
    'PH' : {
        'valueInit' : '',
        'settable' : False,
    },
    'PR' : {
        'valueInit' : 0,
        'format' : '-60000:120000',
        'unit' : "mircosteps",
    },
    'RS' : {
        'valueInit' : False,
        'readable' : False,
    },
    'SA' : {
        'valueInit' : 0,
        'format' : '0:255',
        'readable' : False,
    },
    'SL' : {
        'valueInit' : -60000,
        'format' : '-60000:120000',
        'unit' : "mircosteps",
    },
    'SR' : {
        'valueInit' : -60000,
        'format' : '-60000:120000',
        'unit' : "mircosteps",
    },
    'SM' : {
        'valueInit' : False,
        'readable' : False,
    },
    'ST' : {
        'valueInit' : False,
        'readable' : False,
    },
    'TE' : {
        'valueInit' : 0,
        'settable' : False,
    },
    'TP' : {
        'valueInit' : 0,
        'settable' : False,
        'unit' : "mircosteps",
    },
    'TS' : {
        'valueInit' : 0,
        'settable' : False,
    },
    'VA' : {
        'valueInit' : 0.,
        'format' : '0:200',
        'unit' : "steps/s",
    },
    'VU' : {
        'valueInit' : 0.,
        'format' : '0:200',
        'unit' : "steps/s",
    },
    'VE' : {
        'valueInit' : '',
        'settable' : False,
    },
}

class DeviceClass(scpiPackage.DeviceClass):
    def init_scpi_pre(self):
        self.devisor.runningConnections.opened[','.join(self.address.split(',')[1:])].instr.baudrate = 19200
        self.preSymbol = self.address.split(',')[-1]
        del(self.initNodes['config']['idn'])
        self.initNodes['config']['order'].remove('idn')
        self.scpiDict = scpiDict.copy()


    def scpi_read(self, pB):
        reply = pB.dev.instr.ask(pB.variables['scpi']+'?')
        pB.payload = reply.split(' ')[-1]
        pB.value = pB.convert_payload()

    def scpi_write(self, pB):
        value = pB.convert_value()
        pB.dev.instr.write(pB.variables['scpi']+value)
        pB.publish_value()

    def scpi_trigger(self, pB):
        if pB.value:
            pB.dev.instr.write(pB.variables['scpi'])
        pB.value = False
        pB.publish_value()
