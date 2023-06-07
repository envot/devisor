#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@schueppi.com

import time

from devisor.devisorbase import devisor_import

scpiPackage = devisor_import(None, 'scpi', 'device')

scpiDict = {
    'system:beep:state' : {
        'name' : 'Beep state',
        'valueInit' : True,
        'settable' : True,
    },
    'system:beeper:immediate' : {
        'name' : 'Beep',
        'valueInit' : False,
        'settable' : True,
        'readable' : False,
    },
    'system:error:next' : {
        'name' : 'System error',
        'valueInit' : '',
        'settable' : False,
    }
}

scpiSpecialDict = {
    'source<c>:voltage' : {
        'name' : 'Target voltage',
        'valueInit' : 0.,
        'format' : "0:32.05",
        'settable' : True,
        'unit': 'V'
    },
    'source<c>:current' : {
        'name' : 'Target current',
        'valueInit' : 0.005,
        'format' : "0.0005:10",
        'settable' : True,
        'unit': 'A'
    },
    'output<c>:state' : {
        'name' : 'Output channel',
        'valueInit' : True,
        'settable' : True,
    },
    'output:master' : {
        'name' : 'Output master',
        'valueInit' : True,
        'settable' : True,
    },
    'measure<c>:voltage' : {
        'name' : 'Measured voltage',
        'valueInit' : 0.,
        'format' : "0:32.05",
        'settable' : False,
        'unit': 'V'
    },
    'measure<c>:current' : {
        'name' : 'Measured current',
        'valueInit' : 0.,
        'format' : "0:10",
        'settable' : False,
        'unit': 'A'
    },
    'measure<c>:power' : {
        'name' : 'Measured power',
        'valueInit' : 0.,
        'format' : "0:100",
        'settable' : False,
        'unit': 'W'
    },
}

class DeviceClass(scpiPackage.DeviceClass):
    def init_scpi_pre(self):
        self.scpiDict = scpiDict.copy()
        self.scpiSpecialDict = scpiSpecialDict.copy()
        self.idn = self.instr.ask("*IDN?")
        self.idnArray = self.idn.split(',')
        self.channels = []
        for i in range(int(self.idnArray[1][-1])):
            self.channels.append(str(i+1))
        self._init_special_scpi_dict()


    def _init_special_scpi_dict(self):
        for cmd in self.scpiSpecialDict:
            for i,chan in enumerate(self.channels):
                chanstr = str(chan)
                cmdstr = self._insert_channels(cmd, chanstr)
                paramDict = { 'brokerInit': False }
                paramDict.update(self.scpiSpecialDict[cmd])
                name = cmdstr.replace(':','/')
                if not ('settable' in paramDict):
                    paramDict['settable'] = True
                if not ('readable' in paramDict):
                    paramDict['readable'] = True
                if paramDict['readable']:
                    self.scpi_readables.append(name)
                    if type(paramDict['valueInit']) == bool:
                        paramDict['device_func'] = self.scpi_special_read_bool
                    else:
                        paramDict['device_func'] = self.scpi_special_read
                    if paramDict['settable']:
                        if type(paramDict['valueInit']) == bool:
                            paramDict['broker_func'] = self.scpi_write_bool
                        else:
                            paramDict['broker_func'] = self.scpi_special_write
                else:
                    paramDict['broker_func'] = self.scpi_trigger
                paramDict['variables'] = {'scpi' : self.preSymbol+cmdstr}
                paramDict['variables']['channel'] = chan
                self.create_property(name, scpiPackage.SCPI_CMD_FOLDER, paramDict)

    def scpi_special_read(self, pB):
        pB.dev.instr.write('INST:NSEL ' + str(pB.variables['channel']))
        pB.payload = pB.dev.instr.ask(pB.variables['scpi']+'?')
        pB.value = pB.convert_payload()

    def scpi_special_write(self, pB):
        pB.dev.instr.write('INST:NSEL ' + str(pB.variables['channel']))
        value = pB.convert_value()
        pB.dev.instr.write(pB.variables['scpi']+' '+value)
        pB.publish_value()
    
    def scpi_special_read_bool(self, pB):
        pB.dev.instr.write('INST:NSEL ' + str(pB.variables['channel']))
        pB.payload = pB.dev.instr.ask(pB.variables['scpi']+'?')
        if pB.payload in scpiPackage.SCPI_TRUES:
            pB.value = True
        else:
            pB.value = False

    def scpi_trigger(self, pB):
        if pB.value:
            pB.dev.instr.write(pB.variables['scpi'])
        pB.value = False
        pB.publish_value()

