#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time

from devisor.devisorbase import devisor_import

scpiPackage = devisor_import(None, 'scpi', 'device')

scpiDict = {
    'gps:position:hold:last' : {
        'valueInit' : '',
        'settable' : False,
    },
    'gps:reference:traim:rsvids' : {
        'valueInit' : 0.,
        'settable' : False,
    },
    'gps:reference:pulse:sawtooth' : {
        'valueInit' : 0.,
		'unit' : 'ns',
		'format' : '-128:127',
        'settable' : False,
    },
    'gps:reference:pulse:accuracy' : {
        'valueInit' : 0.,
		'unit' : 'ns',
		'format' : '0:65635',
        'settable' : False,
    },
    'gps:reference:pulse' : {
        'valueInit' : 0,
        'settable' : False,
    },
    # somehow not working. Command not found
    'gps:satellite:tracking:count' : {
        'valueInit' : 0.,
        'settable' : False,
    },
    'gps:satellite:visible:count' : {
        'valueInit' : 0.,
        'settable' : False,
    },
    'ptime:tzone' : {
        'valueInit' : '',
        'settable' : False,
    },
    'ptime:date' : {
        'valueInit' : '',
        'settable' : False,
    },
    'ptime:time' : {
        'valueInit' : '',
        'settable' : False,
    },
    # Note: in the manual they wrongly stated synchronization with z
    'synchronisation:holdover:duration' : {
        'valueInit' : 0.,
		'unit' : 's',
        'settable' : False,
    },
    'synchronisation:source:state' : {
        'valueInit' : '',
        'settable' : False,
    },
    'synchronisation:tinterval' : {
        'valueInit' : 0.,
        'settable' : False,
    },
    'synchronisation:feestimate' : {
        'valueInit' : 0.,
        'settable' : False,
    },
    'synchronisation:locked' : {
        'valueInit' : False,
        'settable' : False,
    },
    'diagnostic:roscillator:efcontrol:relative' : {
        'valueInit' : 0.,
		'unit' : '%',
		'format' : '-100:100',
        'settable' : False,
    },
    'measure:temperature' : {
        'valueInit' : 0.,
		'unit' : 'C',
        'settable' : False,
    },
    'measure:volt' : {
        'valueInit' : 0.,
		'unit' : 'V',
        'settable' : False,
    },
    'measure:current' : {
        'valueInit' : 0.,
		'unit' : 'A',
        'settable' : False,
    },
}

class DeviceClass(scpiPackage.DeviceClass):
    def init_scpi_pre(self):
        self.scpiDict = scpiDict
        self.multiCmd = False

    def scpi_read_bool(self, pB):
        self.scpi_read(pB)

    def scpi_read(self, pB):
        self.attempt = 1
        self.read_convert_furyData(pB)
        pB.value = pB.convert_payload()

    def read_convert_furyData(self, pB):
        try:
            pB.dev.instr.read()
            dataFury = pB.dev.instr.ask(pB.variables['scpi']+'?')
            dataFuryArr = dataFury.split('\r\n')
            if dataFury[-6:] != 'scpi > ':
                time.sleep(0.2)
                dataFury += pB.dev.instr.read()
            if pB.param in ['scpi/measure/current', 'scpi/measure/volt', 'scpi/measure/temperature', 'scpi/gps/reference/traim/rsvids','scpi/gps/reference/pulse','scpi/gps/reference/pulse/sawtooth','scpi/gps/reference/pulse/accuracy', 'scpi/gps/satellite/tracking/count', 'scpi/gps/satellite/visible/count', 'scpi/synchronisation/feestimate', 'scpi/synchronisation/tinterval', 'scpi/synchronisation/source/state', 'scpi/diagnostic/roscillator/efcontrol/relative', 'scpi/ptime/time', 'scpi/ptime/date', 'scpi/ptime/tzone']:
                pB.payload = dataFuryArr[1].replace('%','')
            elif pB.param == 'scpi/synchronisation/holdover/duration':
                pB.payload = dataFuryArr[1].split(',')[0]
            elif pB.param == 'scpi/gps/position/hold/last':
                pB.payload = ';'.join(dataFuryArr[1:4]).replace('\r','').replace('\n','')
            elif pB.param == 'scpi/synchronisation/locked':
                if '1' in dataFury:
                    pB.payload = 'true'
                elif '0' in dataFury:
                    pB.payload = 'false'
                else:
                    self.log.new_log(('No 0, no 1: %s' % dataFury),
                        "ERROR")
            else:
                pB.payload = dataFury
        except:
            self.attempt += 1
            # first readout fails rather often
            if self.attempt < 5:
                self.read_convert_furyData(pB)
            else:
                self.log.new_log(('No Fury data format after 5 attempts: %s' % dataFury),
                        "ERROR")

    def scpi_write(self, pB):
        value = pB.convert_value()
        pB.dev.instr.write(pB.variables['scpi']+' '+value)
        pB.publish_value()
