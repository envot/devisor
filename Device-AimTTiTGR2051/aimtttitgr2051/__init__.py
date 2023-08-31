#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time

from devisor.devisorbase import devisor_import

scpiPackage = devisor_import(None, 'scpi', 'device')

scpiDict = {
    'system:beeper' : {
        'valueInit' : False,
    },
    'system:backlight' : {
        'valueInit' : 0,
        'format' : '0:100',
    },
    'system:version' : {
        'valueInit' : '',
        'settable' : False,
    },
    'frequency' : {
        'valueInit' : 0.,
        'format' : '0:1500000',
        'unit' : 'Hz',
    },
    'power' : {
        'valueInit' : 0.,
        'format' : '-40:10',
        'unit' : 'Hz',
    },
    'source:roscillator:source' : {
        'valueInit' : 'EXT',
        'format' : 'EXT:INT',
        'datatype' : 'enum',
    },
    'source:lowspur' : {
        'valueInit' : True,
    },
    'unit:power' : {
        'valueInit' : 'DBM',
        'format' : 'DBM:DBUV:UV:MV',
        'datatype' : 'enum',
    },
    'output:state' : {
        'valueInit' : False,
    },
}

class DeviceClass(scpiPackage.DeviceClass):
    def init_scpi_pre(self):
        self.scpiDict = scpiDict
