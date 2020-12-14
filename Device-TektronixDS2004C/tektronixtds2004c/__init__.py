#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time

from devisor.devisorbase import devisor_import

scpiPackage = devisor_import(None, 'scpi', 'device')

scpiDict = {
    'horizontal:main:position' : {
        'valueInit' : 0.,
        'unit' : "s",
    },
    'horizontal:main:scale' : {
        'valueInit' : 0.,
        'unit' : "s/div",
    },
    'trigger:main:level' : {
        'valueInit' : 0.,
        'unit' : "volt",
    },
    'trigger:main:mode' : {
        'valueInit' : 'NORMal',
        'format' : "AUTO,NORMal",
        'datatype' : 'enum',
    },
    'trigger:main:edge:source' : {
        'valueInit' : 'CH1',
        'format' : "CH1,CH2,CH3,CH4,EXT,EXT5,AC LINE",
        'datatype' : 'enum',
    },
    'trigger:main:frequency' : {
        'valueInit' : 0.,
        'settable' : False,
    },
    'trigger:state' : {
        'valueInit' : 'AUTO',
        'format' : "ARMED,READY,TRIGGER,AUTO,SAVE,SCAN",
        'datatype' : 'enum',
        'settable' : False,
    },
    'measurement:meas<x>:value' : {
        'valueInit' : 1.,
    },
    'measurement:meas<x>:source' : {
        'valueInit' : 'CH1',
        'format' : "CH1,CH2,CH3,CH4,MATH",
        'datatype' : 'enum',
    },
    'measurement:meas<x>:type' : {
        'valueInit' : 'NONe',
        'format' : "CRMs,CURSORRms,DELay,FALL,FREQuency,MAXImum,MEAN,MINImum,NONe,NWIdth,PDUty,PERIod,PHAse,PK2pk,PWIdth,RISe",
        'datatype' : 'enum',
    },
    'measurement:meas<x>:unit' : {
        'valueInit' : 'NONe',
        'format' : "V,s,Hz,0,A,VA,AA,VV",
        'datatype' : 'enum',
        'settable' : False,
    },
    'ch<a>:bandwidth' : {
        'valueInit' : True,
    },
    'ch<a>:coupling' : {
        'valueInit' : 'DC',
        'format' : "AC,DC,GND",
        'datatype' : 'enum',
    },
    'ch<a>:currentprobe' : {
        'valueInit' : '1',
        'format' : "0.2,1,2,5,10,50,100,1000",
        'datatype' : 'enum',
    },
    'ch<a>:invert' : {
        'valueInit' : False,
    },
    'ch<a>:position' : {
        'valueInit' : 0.,
    },
    'ch<a>:probe' : {
        'valueInit' : '1',
        'format' : "1,10,20,50,100,500,1000",
        'datatype' : 'enum',
    },
    'ch<a>:scale' : {
        'valueInit' : 1.,
        'format' : '2e-3:5',
        'unit' : 'volts/div',
    },
    'ch<a>:yunit' : {
        'valueInit' : 'V',
        'format' : "V,A",
        'datatype' : 'enum',
    },
}

class DeviceClass(scpiPackage.DeviceClass):
    def init_scpi_pre(self):
        self.scpiDict = scpiDict.copy()
        self.measures = 5
        self.analogs = 4