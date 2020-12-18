#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time

from devisor.devisorbase import devisor_import

scpiPackage = devisor_import(None, 'scpi', 'device')

scpiDict = {
    'coupling<a>:ampl:deviation' : {
        'valueInit' : 0.,
        'unit' : "Vpp",
    },
    'coupling<a>:ampl:mode' : {
        'valueInit' : 'RATio',
        'format' : 'OFFSet,RATio',
        'datatype' : 'enum',
    },
    'coupling<a>:ampl:ratio' : {
        'valueInit' : 1.,
        'format' : '0.001:1000',
    },
    'coupling<a>:ampl:state' : {
        'valueInit' : False,
    },
    'coupling<a>:frequency:deviation' : {
        'valueInit' : 0.,
        'format' : '-99999999.9999:99999999.9999',
    },
    'coupling<a>:frequency:mode' : {
        'valueInit' : 'RATio',
        'format' : 'OFFSet:RATio',
        'datatype' : 'enum',
    },
    'coupling<a>:frequency:ratio' : {
        'valueInit' : 1.,
        'format' : '0.000001:1000000',
    },
    'coupling<a>:frequency:state' : {
        'valueInit' : False,
    },
    'coupling<a>:phase:deviation' : {
        'valueInit' : 0.,
        'format' : '-360:360',
    },
    'coupling<a>:phase:mode' : {
        'valueInit' : 'RATio',
        'format' : 'OFFSet,RATio',
        'datatype' : 'enum',
    },
    'coupling<a>:phase:ratio' : {
        'valueInit' : 1.,
        'format' : '0.01:100',
    },
    'coupling<a>:frequency:state' : {
        'valueInit' : False,
    },
    'output<a>:impedance' : {
        'valueInit' : 50,
        'format' : '1:10000',
    },
    'output<a>:polarity' : {
        'valueInit' : 'NORMal',
        'format' : 'NORMal,INVerted',
        'datatype' : 'enum',
    },
    'output<a>:state' : {
        'valueInit' : False,
    },
    'source<a>:apply' : {
        'valueInit' : '',
        'settable' : False,
    },
    'source<a>:frequency:fixed' : {
        'valueInit' : 1e3,
        'format' : '1e-6:100e6',
    },
    'source<a>:phase:adjust' : {
        'valueInit' : 0.,
        'format' : '0:360',
    },
    'source<a>:voltage:level' : {
        'valueInit' : 2e-3,
        'format' : '1e-3:0.15',
        'unit' : "Vpp",
    },
    'source<a>:voltage:offset' : {
        'valueInit' : 0.,
        'format' : '-5:5',
        'unit' : "V",
    },
}

class DeviceClass(scpiPackage.DeviceClass):
    def init_scpi_pre(self):
        self.scpiDict = scpiDict
        self.analogs = 2
