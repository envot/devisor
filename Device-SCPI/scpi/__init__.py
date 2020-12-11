#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time
from threading import Timer

from devisor.devisorbase import DeviceBase

SCPI_CMD_FOLDER = 'scpi'
SCPI_TRUES = ['1', 'ON', 'TRUE', 'True', 'true']

scpiDict = {
    '*IDN?' : {
        'valueInit' : '',
    },
}


control = {}
def control_raw_command(pB):
    if '?' in  pB.value:
        pB.value = pB.dev.instr.ask(pB.value)
        pB.publish_value()
    else:
        pB.dev.instr.send(pB.value)
control['command/raw'] = {
    'valueInit' : '',
    'settable' : True,
}

def control_change_read_interval(pB):
    if pB.dev.ReadOutThread.isAlive():
        pB.dev.ReadOutThread.cancel()
    pB.dev.device_thread()
control['read/interval'] = {
    'valueInit' : 5.,
    'brokerInit' : True,
    'format' : "0.5:1000000",
    'settable' : True,
    'unit': 's',
}
control['read/selection'] = {
    'valueInit': [],
    'brokerInit' : True,
}

def control_read_add(pB):
    if not (pB.value is 'Choose' 
            or pB.value in pB.dev.params['control/read/selection'].value):
        pB.dev.params['control/read/selection'].value.append(pB.value)
        pB.dev.params['control/read/remove/$format'].value = pB.dev.params['control/read/selection'].value + ['Choose']
        pB.dev.params['control/read/remove/$format'].publish_value()
        pB.value = 'Choose'
        pB.publish_value()
control['read/add'] = {
    'valueInit' : 'Choose',
    'datatype' : 'enum',
    'format' : ['Choose'],
    'settable' : True,
    'broker_func': control_read_add,
}
def control_read_remove(pB):
    if (not pB.value is 'Choose' 
            and pB.value in pB.dev.params['control/read/selection'].value):
        pB.dev.params['control/read/selection'].value.remove(pB.value)
        pB.dev.params['control/read/remove/$format'].value = pB.dev.params['control/read/selection'].value + ['Choose']
        pB.dev.params['control/read/remove/$format'].publish_value()
        pB.value = 'Choose'
        pB.publish_value()
control['read/remove'] = {
    'valueInit' : 'Choose',
    'datatype' : 'enum',
    'format' : ['Choose'],
    'settable' : True,
    'broker_func': control_read_remove,
}

def control_read_selection(pB):
    for cmd in pB.dev.scpi_readables:
        pB.dev.read_selection()
    pB.value = False
    pB.publish_value()
control['read/selected'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : control_read_selection,
}

def control_read_all(pB):
    for cmd in pB.dev.scpi_readables:
        pB.dev.params[SCPI_CMD_FOLDER+'/'+cmd.replace(':','/')].device('?')
    pB.value = False
    pB.publish_value()
control['read'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : control_read_all,
}



config = {}
def config_save(pB):
    if pB.value:
        confName = 'config/saved/'+pB.value
        confDict = {}
        for cmd in pB.dev.scpi_readables:
            name = SCPI_CMD_FOLDER+'/'+cmd.replace(':','/')
            confDict[cmd] = pB.dev.params[name].value
        if confName in pB.dev.params:
            pB.dev.params[confName].device(confDict)
        else:
            initDict = {
                'valueInit' : confDict,
                'brokerInit' : False,
            }
            pB.dev.create_property('saved/'+pB.value, 'config', initDict)
            pB.dev.params['config/load/$format'].value.append(pB.value)
            pB.dev.params['config/load/$format'].publish_value()
        pB.value = ''
        pB.publish_value()
config['save'] = {
    'valueInit' : '',
    'broker_func' : config_save,
    'brokerInit' : False,
    'settable' : True,
}

def config_load(pB):
    confName = 'config/saved/'+pB.value
    if confName in pB.dev.params:
        confDict = pB.dev.params[confName].value
        cmdMultiStr = ''
        for cmd in confDict:
            if cmd in pB.dev.scpi_readables:
                name = SCPI_CMD_FOLDER + cmd.replace(':','/')
                param = pB.dev.params[name]
                param.device(confDict[cmd])
                if param.value != param.valueOld:
                    cmdMultiStr += ';'+cmd+' '+confDict[cmd]
        pB.dev.instr.write(cmdMultiStr)
    pB.value = ''
    pB.publish_value()
config['load'] = {
    'valueInit' : 'Choose',
    'broker_func' : config_load,
    'brokerInit' : False,
    'format' : ['Choose'],
    'datatype' : 'enum',
}

def config_remove(pB):
    if pB.value:
        try:
            pB.dev.remove_property('saved/'+pB.value, 'config')
            pB.dev.params['config/load/$format'].value.remove(pB.value)
            pB.dev.params['config/load/$format'].publish_value()
        except Exception:
            _, err, _ = sys.exc_info()
            pB.new_log('Could not remove'
                +'config/saved/'+pB.value+ ': ' + err)
        pB.value = ''
        pB.publish_value()
config['remove'] = {
    'valueInit' : '',
    'broker_func' : config_remove,
    'brokerInit' : False,
    'settable' : True,
}

def config_id(pB):
    pB.value = pB.dev.instr.ask("*IDN?")
    pB.publish_value()
config['idn'] = {
    'valueInit' : 'IDN',
    'device_func' : config_id,
    'brokerInit' : False,
    }



class DeviceClass(DeviceBase):
    def init_pre(self):
        self.instr = self.devisor.runningConnections.open(self.address)
        self.measures = 5
        self.digitals = 8
        self.analogs = 4
        self.preSymbol = ':'
        self.initNodes = {}
        self.initNodes['control'] = control.copy()
        self.initNodes['control']['order'] = ['read', 'read/interval', 'read/selection', 'read/remove', 'read/add', 'read/selected']
        self.initNodes['config'] = config.copy()
        self.initNodes['config']['order'] = ['idn', 'save', 'load', 'remove']
        self.init_scpi_pre()
        self._init_scpi_dict()
        self.initNodes['control']['read/add']['format'] = ['Choose'] + self.scpi_readables

    def init_scpi_pre(self):
        self.scpiDict = scpiDict

    def device_thread(self):
        self.ReadOutThread = Timer(self.params['control/read/interval'].value, self.read_selection)
        self.ReadOutThread.start()

    def init_after(self):
        self._init_config_saved()
        self.init_scpi_after()

    def init_scpi_after(self):
        pass

    def read_selection(self):
        multiCmdArray = self.params['control/read/selection'].value
        if len(multiCmdArray) > 0:
            multiCmdStr = '?;:'.join(multiCmdArray).replace('/',':') + '?'
            multiReply = self.instr.ask(multiCmdStr)
            for i,reply in enumerate(multiReply.split(';')):
                param = SCPI_CMD_FOLDER+'/'+multiCmdArray[i]
                self.params[param].payload = reply
                self.params[param].value = self.params[param].convert_payload()
                self.params[param].publish_value()
        self.device_thread()

    def scpi_read(self, pB):
        pB.payload = pB.dev.instr.ask(pB.variables['scpi']+'?')
        pB.value = pB.convert_payload()

    def scpi_write(self, pB):
        value = pB.convert_value()
        pB.dev.instr.write(pB.variables['scpi']+' '+value)
        pB.publish_value()
    
    def scpi_read_bool(self, pB):
        pB.payload = pB.dev.instr.ask(pB.variables['scpi']+'?')
        if pB.payload in SCPI_TRUES:
            pB.value = True
        else:
            pB.value = False
    
    def scpi_write_bool(self, pB):
        if pB.value:
            pB.dev.instr.write(pB.variables['scpi']+' '+SCPI_TRUES[0])
        else:
            pB.dev.instr.write(pB.variables['scpi']+' 0')
    
    def scpi_trigger(self, pB):
        if pB.value:
            pB.dev.instr.write(pB.variables['scpi']+' '+SCPI_TRUES[0])
        pB.value = False
        pB.publish_value()

    def _init_scpi_dict(self):
        self.scpi_readables = []
        for cmd in self.scpiDict:
            channels = [0]
            if '<a>' in cmd:
                channels = list(range(1,self.analogs+1))
            if '<x>' in cmd:
                channels = list(range(1,self.measures+1))
            if '<d>' in cmd:
                channels = list(range(self.digitals))
            for i,chan in enumerate(channels):
                chanstr = str(chan)
                cmdstr = cmd.replace('<a>', chanstr)
                cmdstr = cmdstr.replace('<x>', chanstr)
                cmdstr = cmdstr.replace('<d>', chanstr)
                paramDict = { 'brokerInit': False }
                paramDict.update(self.scpiDict[cmd])
                name = cmdstr.replace(':','/')
                if not ('settable' in paramDict):
                    paramDict['settable'] = True
                if not ('readable' in paramDict):
                    paramDict['readable'] = True
                if paramDict['readable']:
                    self.scpi_readables.append(name)
                    if type(paramDict['valueInit']) == bool:
                        paramDict['device_func'] = self.scpi_read_bool
                    else:
                        paramDict['device_func'] = self.scpi_read
                    if paramDict['settable']:
                        if type(paramDict['valueInit']) == bool:
                            paramDict['broker_func'] = self.scpi_write_bool
                        else:
                            paramDict['broker_func'] = self.scpi_write
                else:
                    paramDict['broker_func'] = self.scpi_trigger
                paramDict['variables'] = {'scpi' : self.preSymbol+cmdstr}
                self.create_property(name, SCPI_CMD_FOLDER, paramDict)

    def _init_config_saved(self):
        savedConfigs = []
        for initTopic in self.initBrokerMsgs:
            if initTopic[:13] == 'config/saved/':
                savedConfig = self.initBrokerMsgs[initTopic].split('/')[-1]
                savedConfigs.append(savedConfig)
                initDict = {
                    'valueInit' : {},
                    'brokerInit' : True,
                }
                self.create_property('saved/'+savedConfig, 'config', initDict)
        self.params['config/load/$format'].value = savedConfigs + ['Choose']
        self.params['config/load/$format'].publish_value()

    def exit_pre(self):
        self.ReadOutThread.cancel()
