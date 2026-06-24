#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time
from threading import Timer

from devisor.devisorbase import devisor_import

scpiPackage = devisor_import(None, 'scpi', 'device')

scpiDict = {
    'system:error:count' : {
        'valueInit' : 0,
        'settable' : False,
    },
    'system:version' : {
        'valueInit' : '',
        'settable' : False,
    },
    'measure<a>:temperature1' : {
        'valueInit' : '0.',
        'unit' : 'deg',
        'settable' : False,
    },
    'measure<a>:temperature2' : {
        'valueInit' : '0.',
        'unit' : 'deg',
        'settable' : False,
    },
    'measure<a>:current' : {
        'valueInit' : '0.',
        'unit' : 'mA',
        'settable' : False,
    },
    #'measure<a>:voltage' : { #6 has not voltage
    #    'valueInit' : '0.',
    #    'unit' : 'V',
    #    'settable' : False,
    #},
    #'measure6:optical' : { # not working
    #    'valueInit' : '0.',
    #    'unit' : 'W',
    #    'settable' : False,
    #},
    #'measure7:temperature' : { # not working
    #    'valueInit' : '0.',
    #    'unit' : 'deg',
    #    'settable' : False,
    #},
    #'measure7:pressure' : { # not working
    #    'valueInit' : '0.',
    #    'unit' : 'mbar',
    #    'settable' : False,
    #},
    #'measure7:humidity' : { # not working
    #    'valueInit' : '0.',
    #    'unit' : 'percent RH',
    #    'settable' : False,
    #},
    'output<a>:state' : {
        'valueInit' : '0',
    },
    'source<a>:name' : {
        'valueInit' : '',
    },
    'source6:mode' : {
        'valueInit' : '0',
    },
    'source6:current:limit' : {
        'valueInit' : '0.',
        'unit' : 'mA',
    },
    #'source6:current:max' : { # not working
    #    'valueInit' : '0.',
    #    'unit' : 'mA',
    #},
    #'source6:optical:limit' : { # not working
    #    'valueInit' : '0.',
    #    'unit' : 'W',
    #},
}


class DeviceClass(scpiPackage.DeviceClass):
    def init_scpi_pre(self):
        self.scpiDict = scpiDict.copy()
        self.analogs = 6
