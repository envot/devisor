#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time

from devisor.devisorbase import devisor_import

scpiPackage = devisor_import(None, 'scpi', 'device')

scpiDict = {
    'DIA' : {
        'name' : 'Diagnostic report',
        'valueInit' : '',
        'settable' : False,
    },
    'ERR' : {
        'name' : 'Error number',
        'valueInit' : '',
        'settable' : False,
    },
    'FRF' : {
        'name' : 'Reference status',
        'valueInit' : '',
        'settable' : False,
    },
    'HLT' : {
        'name' : 'Halt movement',
        'valueInit' : False,
        'readable' : False,
    },
    'RBT' : {
        'name' : 'Reboot',
        'valueInit' : False,
        'readable' : False,
    },
    'SPI' : {
        'name' : 'Get Pivot Point',
        'valueInit' : '',
        'settable' : False,
    },
    'STP' : {
        'name' : 'Stop movement',
        'valueInit' : False,
        'readable' : False,
    },
    'SVO' : {
        'name' : 'Servo Mode (0=open, 1=closed)',
        'valueInit' : '',
        'settable' : False,
    },
    'VER' : {
        'name' : 'Firmware',
        'valueInit' : '',
        'settable' : False,
    },
    'VER' : {
        'name' : 'Firmware',
        'valueInit' : '',
        'settable' : False,
    },
    'VLS' : {
        'name' : 'System velocity',
        'valueInit' : 0.,
        'settable' : True,
        'format' : "3.84143172295e-05:2.5",
        'unit': 'mm/s'
    },
}

def cmd_axis(pB):
    ax = pB.param.split('/')[1]
    target = pB.param.split('/')[2]
    cmdsKeys = list(pB.dev.cmds.keys())
    cmdsVals = list(pB.dev.cmds.values())
    cmd = cmdsKeys[cmdsVals.index(target)]
    if cmd == 'MOV':
        if pB.dev.moving and pB.dev.params['control/read/interval'].value != 0.1:
            pB.dev.intervalTime = pB.dev.params['control/read/interval'].value
            pB.dev.moving = True
        pB.dev.params['control/read/interval'].publish_value(0.1)
        if pB.dev.ReadOutThread.is_alive():
            pB.dev.ReadOutThread.cancel()
            pB.dev.device_thread()
    pB.dev.instr.write(cmd+' '+ax+' '+str(pB.value))

class DeviceClass(scpiPackage.DeviceClass):
    def init_scpi_pre(self):
        self.intervalTime = 10.
        self.moving= False
        self.scpiDict = scpiDict.copy()
        self.axes = ['x', 'y', 'z', 'u', 'v', 'w']
        self.cmds = {
                'MOV' : 'target',
                'NLM' : 'lower-limit',
                'PLM' : 'higher-limit',
                'POS' : 'position',
                'TMN' : 'min-value',
                'TMX' : 'max-value',
                'ONT' : 'on-target',
                }
        axisInit = {}
        self.units = {}
        for ax in self.axes:
            self.units[ax] = self.instr.ask('PUN? '+ax)[2:]
            for cmd in self.cmds:
                axisInit[ax+'/'+self.cmds[cmd]] = {
                    'valueInit' : 0.,
                    'brokerInit' : False,
                    'settable' : True,
                    'unit' : self.units[ax],
                    'broker_func' : cmd_axis,
                    }
        self.initNodes['axis'] = axisInit

    def init_scpi_after(self):
        self.read_all_axes()

    def scpi_trigger(self, pB):
        if pB.value:
            pB.dev.instr.write(pB.variables['scpi'])
        pB.value = False
        pB.publish_value()

    def read_selection(self):
        onTarget = self.read_all_axes(skip=['target'])
        if onTarget and self.moving:
            self.params['control/read/interval'].publish_value(self.intervalTime)
            self.moving = False
        self.device_thread()

    def read_all_axes(self, skip=[]):
        onTarget = False
        for cmd in self.cmds:
            if not self.cmds[cmd] in skip:
                results = self._convert_axes(cmd)
                if cmd == 'ONT':
                    onTarget = not (0 in results.values())
                for ax in results:
                    self.params['axis/'+ax+'/'+self.cmds[cmd]].value = results[ax]
                    self.params['axis/'+ax+'/'+self.cmds[cmd]].publish_value()
        return onTarget


    def _convert_axes(self, cmd):
        resultArray = self.instr.ask(cmd+'?').split('\n')
        results = {}
        for i,ax in enumerate(self.axes):
            results[ax] = float(resultArray[i][2:])
        return results
