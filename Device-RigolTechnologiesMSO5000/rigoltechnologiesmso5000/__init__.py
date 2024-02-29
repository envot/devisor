#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time
from threading import Timer

from devisor.devisorbase import devisor_import

scpiPackage = devisor_import(None, 'scpi', 'device')
qfpscan = devisor_import(None, 'qfpscan', 'utility')

scpiDict = {
    'timebase:main:offset' : {
        'valueInit' : 0.,
        'unit' : "s",
    },
    'timebase:main:scale' : {
        'valueInit' : 0.,
        'unit' : "s/div",
    },
    'timebase:mode' : {
        'valueInit' : 'main',
        'format' : "main,xy,roll",
        'datatype' : 'enum',
    },
    'trigger:mode' : {
        'valueInit' : 'edge',
        'format' : "edge,pulse,slope,video,pattern,duration,timeout,runt,window,delay,setup,nedge,rs232,iic,spi,can,flexray,lin,iis,m1553",
        'datatype' : 'enum',
    },
    'trigger:coupling' : {
        'valueInit' : 'DC',
        'format' : "AC,DC,LFReject,HFReject",
        'datatype' : 'enum',
    },
    'trigger:status' : {
        'valueInit' : 'RUN',
        'format' : "TD,WAIT,RUN,AUTO,STOP",
        'datatype' : 'enum',
        'settable' : False,
    },
    'trigger:edge:source' : {
        'valueInit' : 'channel1',
        'format' : "D0,D1,D2,D3,D4,D5,D6,D7,D8,D9,D10,D11,D12,D13,D14,D15,D1,channel1,channe2,channel3,channel4,ACLine",
        'datatype' : 'enum',
    },
    'measure:source' : {
        'valueInit' : 'channel1',
        'format' : "D0,D1,D2,D3,D4,D5,D6,D7,D8,D9,D10,D11,D12,D13,D14,D15,D1,channel1,channe2,channel3,channel4,math1,math2,math3,math4",
        'datatype' : 'enum',
    },
    'measure:clear' : {
        'valueInit' : 'none',
        'format' : "item1,item2,item3,item4,item5,item6,item7,item8,item9,item10,all",
        'datatype' : 'enum',
        'readable' : False,
    },
    'measure:statistic:display' : {
        'valueInit' : False,
    },
    'measure:statistic:reset' : {
        'valueInit' : False,
        'readable' : False,
    },
    'measure:mode' : {
        'valueInit' : 'noraml',
        'format' : "normal,precision",
        'datatype' : 'enum',
        'readable' : False,
    },
    #'measure:statistic:item' : {
    #    'valueInit' : 'Vmax',
    #    'format' : "Vmax,Vmin,Vpp,Vtop,Vbase,Vamp,Vavg,Vrms,overshoot,preshoot,Marea,MParea,period,frequency,Rtime,Ftime,Pwidth,Nwidth,Pduty,Nduty,TVmax,TVmin,Pslewrate,Nslewrate,Vupper,Vmid,Vlower,variance,PVrms,Ppulses,Npulses,Pedges,Nedges,RRdelay,RFdelay,FRdelay,FFdelay,RRphase,RFphase,FRphase,FFphase", # sometime sources are needen... manual p. 2-119
    #    # need to at type: max,min,current,averages
    #    'datatype' : 'enum',
    #},
    #'measure:item' : {
    #    'valueInit' : 'Vmax',
    #    'format' : "Vmax,Vmin,Vpp,Vtop,Vbase,Vamp,Vavg,Vrms,overshoot,preshoot,Marea,MParea,period,frequency,Rtime,Ftime,Pwidth,Nwidth,Pduty,Nduty,TVmax,TVmin,Pslewrate,Nslewrate,Vupper,Vmid,Vlower,variance,PVrms,Ppulses,Npulses,Pedges,Nedges,RRdelay,RFdelay,FRdelay,FFdelay,RRphase,RFphase,FRphase,FFphase", # sometime sources are needen... manual p. 2-120
    #    'datatype' : 'enum',
    #},
    'measure:area' : {
        'valueInit' : 'main',
        'format' : "main,zoom,cursor",
        'datatype' : 'enum',
    },
    'channel<a>:bwlimit' : {
        'valueInit' : 'OFF',
        'format' : "20M,off",
        'datatype' : 'enum',
    },
    'channel<a>:coupling' : {
        'valueInit' : 'DC',
        'format' : "AC,DC,GND",
        'datatype' : 'enum',
    },
    'channel<a>:display' : {
        'valueInit' : False,
    },
    'channel<a>:invert' : {
        'valueInit' : False,
    },
    'channel<a>:offset' : {
        'valueInit' : 0.,
        'unit': "V"
    },
    'channel<a>:scale' : {
        'valueInit' : 1.,
        'format' : '10e-3:100',
        'unit' : 'V/div',
    },
    'channel<a>:probe' : {
        'valueInit' : '1',
        'format' : "0.0001,0.0002,0.0005,0.001,0.002,0.005,0.01,0.02,0.05,0.1,0.2,0.5,1,2,5,10,20,50,100,200,500,1000,2000,5000,10000,20000,50000",
        'datatype' : 'enum',
    },
    'channel<a>:units' : {
        'valueInit' : 'voltage',
        'format' : "voltage,watt,ampere,unknown",
        'datatype' : 'enum',
    },
    'channel<a>:vernier' : {
        'valueInit' : False,
    },
    'channel<a>:position' : {
        'valueInit' : 0.,
        'format' : '-100:100',
        'unit': "V"
    },
}

measures = {}
measures['list'] = {
        'valueInit' : '',
        'settable' : True,
        'brokerInit' : True
}
def read_measures(pB):
    pB.dev.read_selected_measures()
    pB.publish_value(False)
measures['read'] = {
        'valueInit' : False,
        'settable' : True,
        'broker_func' : read_measures
}
def control_change_read_measures_interval(pB):
    if pB.dev.up:
        if pB.dev.ReadOutMeasuresThread.is_alive():
            pB.dev.ReadOutMeasuresThread.cancel()
        pB.dev.device_measures_thread()

measures['interval'] = {
    'valueInit' : 60.,
    'brokerInit' : True,
    'broker_func' : control_change_read_measures_interval,
    'format' : "0.5:1000000",
    'settable' : True,
    'unit': 's',
}



#waveform = {}
#TBC
#def waveform_acquire(pB):
#    pB.dev.waveform_acquire()
#    pB.value = False
#waveform['acquire'] = {
#        'valueInit' : False,
#        'settable' : True,
#        'broker_func' : waveform_acquire
#}
#waveform['channels'] = {
#        'valueInit' : ['CH1'],
#        'brokerInit' : True,
#        'settable' : True,
#}

class DeviceClass(scpiPackage.DeviceClass):
    def init_scpi_pre(self):
        self.scpiDict = scpiDict.copy()
        self.initNodes['measures'] = measures
        self.initNodes['measures']['order'] = ['list', 'read', 'interval']
        self.measures = 5
        self.analogs = 4
        #self.initNodes['waveform'] = waveform

    def init_scpi_after(self):
        self.device_measures_thread()

    def device_measures_thread(self):
        self.ReadOutMeasuresThread = Timer(self.params['measures/interval'].value,
                                           self.read_selected_measures_loop)
        self.ReadOutMeasuresThread.start()

    def read_selected_measures(self):
        for cmdPart in self.params['measures/list'].value.split(';'):
            try:
                value = self.dev.instr.ask(":measure:statistic:item? "+cmdPart)
                self.dev.publish_topic('measures/results/'+cmdPart, value.replace(',','-'))
            except:
                self.dev.log.new_log('Could not read measures:statistic:item '+cmdPart, 'INFO')

    def read_selected_measures_loop(self):
        self.read_selected_measures()
        self.device_measures_thread()

    #def waveform_acquire(self):
    #    #self.instr.write('data:encdg RIBinary')
    #    self.instr.write('acquire:state off')
    #    self.instr.write('data:encdg ASCII')
    #    self.instr.write('data:width 1')
    #    self.instr.write('data:start 1')
    #    self.instr.write('data:stop 2500')
    #    datadicts = []
    #    wfmpre = self.instr.ask('wfmpre?').split(';')
    #    predata  = list(range(0,2500))
    #    data = [x * float(wfmpre[8])*1e3 - float(wfmpre[9]) - float(wfmpre[10]) for x in predata]
    #    datadicts.append({
    #        'data' : data,
    #        'name' : 'Time',
    #        'unit' : 'ms',
    #        'unitlong' : 'milliseconds',
    #        'symbol' : 't',})
    #    for channel in self.params['waveform/channels'].value:
    #        self.instr.write('data:source '+channel)
    #        wfmpre = self.instr.ask('wfmpre?').split(';')
    #        datastr = self.instr.ask('curve?')
    #        predata = datastr.split(',')
    #        data = [float(x) * float(wfmpre[12])*1e3 - float(wfmpre[13]) - float(wfmpre[14]) for x in predata]
    #        datadicts.append({
    #            'data' : data,
    #            'name' : channel,
    #            'unit' : 'm'+wfmpre[-1][1],
    #            'unitlong' : 'milli'+wfmpre[-1][1:-1],
    #            'symbol' : 'U',})
    #    self.instr.write('acquire:state on')
    #    newscan = qfpscan.Scan(datadicts, '/mnt/qos/cryotrap/data/')
    #    newscan.settings = {
    #            'Osci.Name': self.name,
    #            'Waveform.Preamble': wfmpre
    #            }
    #    newscan.createFolder()
    #    newscan.save()

    def exit_pre(self):
        self.ReadOutMeasuresThread.cancel()
        self.ReadOutThread.cancel()
