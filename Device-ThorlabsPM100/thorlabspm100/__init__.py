#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@schueppi.com

import time
from threading import Timer

from devisor.devisorbase import devisor_import

scpiPackage = devisor_import(None, 'scpi', 'device')

scpiDict = {
    'sense:correction:wavelength' : {
        'name' : 'Wavelength',
        'valueInit' : 0,
        'settable' : True,
    },
    'sense:power:range:auto' : {
        'name' : 'Auto ranging',
        'valueInit' : 0,
        'settable' : True,
    },
    'sense:power:unit' : {
        'name' : 'Power unit',
        'valueInit' : '',
        'settable' : False,
    },
    'measure:power' : {
        'name' : 'Power',
        'valueInit' : 0.,
        'settable' : False,
    },
    'system:error' : {
        'name' : 'System error',
        'valueInit' : '',
        'settable' : False,
    },
    'system:version' : {
        'name' : 'System version',
        'valueInit' : '',
        'settable' : False,
    },
    'system:sensor:idn' : {
        'name' : 'Sensor IDN',
        'valueInit' : '',
        'settable' : False,
    }
}


def trigger_measure(pB):
    if pB.value:
        pB.dev.params['measure/index'].publish_value(0)
        if pB.dev.ReadOutThread.is_alive():
            pB.dev.ReadOutThread.cancel()
        if pB.dev.MeasureThread.is_alive():
            pB.dev.MeasureThread.cancel()
        pB.dev.measure_thread()
    else:
        if pB.dev.MeasureThread.is_alive():
            pB.dev.MeasureThread.cancel()
        if not pB.dev.ReadOutThread.is_alive():
            pB.dev.device_thread()

def change_index(pB):
    pB.dev.set_index(pB.value)

def change_positions(pB):
    pB.dev.publish_topic('measure/position/$format', ','.join(pB.value))

measure = {
    'active' : {
        'valueInit' : False,
        'brokerInit' : False,
        'settable' : True,
        'broker_func': trigger_measure,
        },
    'repeat' : {
        'valueInit' : False,
        'brokerInit' : True,
        'settable' : True,
        },
    'switch-lasers' : {
        'valueInit' : False,
        'brokerInit' : False,
        'settable' : True,
        },
    'index' : {
        'valueInit' : 0,
        'brokerInit' : False,
        'settable' : True,
        'broker_func' : change_index,
        },
    'points' : {
        'valueInit' : [],
        'brokerInit' : True,
        'settable' : True,
        },
    'laser-links' : {
        'valueInit' : [],
        'brokerInit' : True,
        'settable' : True,
        },
    'waittime-scanpoint' : {
        'valueInit' : 0.5,
        'format' : "0.1:100",
        'brokerInit' : True,
        'settable' : True,
        'unit': 's',
        },
    'waittime-switching' : {
        'valueInit' : 0.5,
        'format' : "0.1:100",
        'brokerInit' : True,
        'settable' : True,
        'unit': 's',
        },
    'waittime-repeat' : {
        'valueInit' : 5,
        'format' : "0.1:100",
        'brokerInit' : True,
        'settable' : True,
        'unit': 's',
        },
    'position' : {
        'valueInit' : 'before-chamber',
        'brokerInit' : True,
        'datatype' : 'enum',
        'format' : ['before-chamber'],
        'settable' : True,
        },
    'positions' : {
        'valueInit' : ['before-chamber'],
        'brokerInit' : True,
        'settable' : True,
        'broker_func': change_positions,
        },
    }


class DeviceClass(scpiPackage.DeviceClass):
    def init_scpi_pre(self):
        self.scpiDict = scpiDict.copy()
        self.initNodes['measure'] = measure
        self.MeasureThread = Timer(1, self.measure_point)

    def measure_thread(self):
        self.MeasureThread = Timer(self.params['measure/waittime-scanpoint'].value,
                self.measure_point)
        self.MeasureThread.start()

    def measure_point(self):
        ind = self.params['measure/index'].value
        wavelength = self.params['measure/points'].value[ind]
        self.set_index(ind)
        power = self.instr.ask('measure:power?')
        self.dev.client.publish('laser-powers/'
                +wavelength+'/'
                +self.params['measure/position'].value,
                power, qos=1,
                retain=True)
        self.switch_lasers()
        if ind+1 >= len(self.params['measure/points'].value):
            if self.params['measure/repeat'].value:
                self.params['measure/index'].publish_value(0)
                time.sleep(self.params['measure/waittime-switching'].value)
            else:
                self.params['measure/active'].publish_value(False)
                return True
        else:
            self.params['measure/index'].publish_value(ind+1)
        if self.params['measure/active'].value:
            self.measure_thread()
        return True

    def set_index(self, ind):
        wavelength = self.params['measure/points'].value[ind]
        self.params['scpi/sense/correction/wavelength'].broker(wavelength)
        if self.params['measure/switch-lasers'].value:
            self.switch_lasers(on=ind)
            time.sleep(self.params['measure/waittime-switching'].value)

    def switch_lasers(self, on=-1):
        for i,link in enumerate(self.params['measure/laser-links'].value):
            payload = 'false'
            if on == i:
                payload = 'true'
            self.dev.client.publish(link+'/set', payload, qos=1, retain=True)
