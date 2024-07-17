#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import sys
import time
from threading import Thread
import asyncio
import ctypes
import numpy as np
from toptica.lasersdk.client import Client, NetworkConnection

from devisor.devisorbase import DeviceBase

class WlmDllCaller(object):
    '''Class for loading the wlmData.dll and calling its functions.'''

    def __init__(self):
        '''Constructor

        @raise WlmError: An error occurred accessing the wavelength meter.
        '''

        # Load DLL into memory.
        try:
            self.wlmDataDll = ctypes.windll.wlmData
        except Exception as e:
            raise WlmError(e)

        self.wlmDataDll.GetFrequencyNum.restype = ctypes.c_double
        self.wlmDataDll.GetPowerNum.restype = ctypes.c_double
        self.wlmDataDll.GetTemperature.restype = ctypes.c_double
        self.wlmDataDll.GetPressure.restype = ctypes.c_double

        if self.wlmDataDll.Instantiate(-1, 0, 0, 0) == 0:
            raise WlmError("wavelength meter software not running")

    def get_pressure(self):
        kack = ctypes.c_double(0)
        pressure = self.wlmDataDll.GetPressure(kack)
        return pressure

    def  get_temperature(self):
        kack = ctypes.c_double(0)
        temp = self.wlmDataDll.GetTemperature(kack)
        return temp

    def get_frequency(self, port):
        port_c = ctypes.c_long(port)
        kack = ctypes.c_double(0)
        value = self.wlmDataDll.GetFrequencyNum(port_c,kack)
        return value 

    def get_power(self, port):
        port_c = ctypes.c_long(port)
        kack = ctypes.c_double(0)
        value = self.wlmDataDll.GetPowerNum(port_c,kack)
        return value

class DLCVolt():
    def __init__(self, dev, host='localhost', portCmd=1998, portMon=1999,
            param= 'laser1:dl:pc:voltage-set'):
        self.dev = dev
        self.param = param
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.client = Client(NetworkConnection(host, portCmd, portMon))
        self.client.open()
        self.retry = 0
        self.maxRetries = 3
        self.value = self.client.get(self.param)

    def set(self, param, value):
        try:
            self.client.set(param, value)
        except:
            if self.retry < self.maxRetries:
                self.retry += 1
                self.set(param, value)
            else:
                self.dev.log.new_log('Could not set error'+param+'.', 'ERROR')
                return False
        self.retry = 0
        return True

    def get(self, param):
        try:
            result = self.client.get(param)
        except:
            if self.retry < self.maxRetries:
                self.retry += 1
                self.get(param)
            else:
                self.dev.log.new_log('Could not get '+param+'.', 'ERROR')
                return False
        self.retry = 0
        return result

    def set_value(self, value):
        self.value = value
        self.set(self.param, self.value)

    def set_value_diff(self, valueDiff):
        self.value += valueDiff
        self.set(self.param, self.value)

    def read_value(self):
        self.value = self.get(self.param)
        return self.value


def set_lock_value(pB):
    lockName = pB.param.split('/')[1]
    pB.dev.locks[lockName].__dict__[pB.name.replace('-','')] = pB.value

def trigger_lock(pB):
    lockName = pB.param.split('/')[1]
    if pB.value:
        pB.dev.locks[lockName].start()
    else:
        pB.dev.locks[lockName].stop()

class LaserLock():
    def __init__(self, dev, name):
        self.name = name
        self.dev = dev
        self.active = False
        self.locked = False

    def init_after(self):
        self.dev.create_property(self.name+'/frequency-set', 'locks', {
            'valueInit': 700.,
            'unit': 'MHz',
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/frequency-shift', 'locks', {
            'valueInit': 0.,
            'unit': 'MHz',
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/wavemeter-channel', 'locks', {
            'valueInit': 1,
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/tolerance', 'locks', {
            'valueInit': 2.,
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/sign', 'locks', {
            'valueInit': 1,
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/factor', 'locks', {
            'valueInit': 1e-3,
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/max-difference', 'locks', {
            'valueInit': 1e-2,
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/laser-param', 'locks', {
            'valueInit' : 'laser1:dl:pc:voltage-set',
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/laser-host', 'locks', {
            'valueInit' : 'localhost',
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/laser-port-command', 'locks', {
            'valueInit' : 1998,
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/laser-port-monitor', 'locks', {
            'valueInit' : 1999,
            'brokerInit': True,
            'broker_func': set_lock_value,
            'settable': True,})
        self.dev.create_property(self.name+'/active', 'locks', {
            'valueInit': False,
            'brokerInit': True,
            'broker_func': trigger_lock,
            'settable' : True,})
        self.dev.create_property(self.name+'/locked', 'locks', {
            'valueInit': False,
            'brokerInit': False,
            'settable' : False,})

    def start(self):
        self.laser = DLCVolt(self.dev, self.laserhost,
                self.laserportcommand,
                self.laserportmonitor,
                param=self.laserparam)
        self.active = True
        self.dev.log.new_log('Lock: {} started'.format(self.name))

    def adj_freq(self, freqNew):
        freqDiff = (self.frequencyset - freqNew)*1e6 + self.frequencyshift # THz to MHz
        laserVoltDiff = self.sign * self.factor * freqDiff
        if abs(freqDiff) > self.tolerance:
            self.locked = False
            self.dev.params['locks/'+self.name+'/locked'].publish_value(False)
            if freqNew < 0:
                self.dev.log.new_log('Error: {}. Switching off lock.'.format(freqNew))
                self.stop()
                return False
            else:
                if abs(laserVoltDiff) > self.maxdifference:
                    self.dev.log.new_log('Laser lock {}: value difference cut.'.format(self.name))
                    laserVoltDiff = np.sign(laserVoltDiff) * self.maxdifference
        else:
            self.locked = True
            self.dev.params['locks/'+self.name+'/locked'].publish_value(True)
        self.laser.set_value_diff(laserVoltDiff)
        return True

    def stop(self):
        if self.active:
            del(self.laser)
        self.active = False
        self.dev.log.new_log('Lock: {} stopped'.format(self.name))


def create_lock(pB):
    pB.publish_value(True)
    name = pB.dev.params['config/lock-name'].value
    pB.dev.create_lock(name)
    pB.value = False

def handle_locks(pB):
    locks2del = []
    for lockName in pB.dev.locks:
        if not lockName in pB.value:
            locks2del.append(lockName)
    for lock2del in locks2del:
        pB.dev.log.new_log('We close '+lock2del+'.')
        del(pB.dev.locks[lock2del])
    for lockName in pB.value:
        if not lockName in pB.dev.locks:
            pB.dev.create_lock(lockName)


config = {}
config['lock-name']={
    'valueInit' : '',
    'brokerInit' : True,
    'settable' : True,
}
config['lock-add']={
    'valueInit' : False,
    'brokerInit' : False,
    'broker_func' : create_lock,
    'settable' : True,
}
config['locks']={
    'valueInit' : [],
    'brokerInit' : True,
    'broker_func' : handle_locks,
    'settable' : True,
}
config['refresh-interval']={
    'valueInit' : 0.01,
    'brokerInit' : True,
    'format' : "0.01:10000",
    'settable' : True,
    'unit': 's',
}

main = {}
main['pressure']={
    'valueInit' : 1000.,
    'brokerInit' : True,
    'format' : "800:1200",
    'unit': 'mbar',
}
main['temperature']={
    'valueInit' : 1000.,
    'brokerInit' : True,
    'format' : "0:50",
    'unit': 'C',
}

channel = {}
for i in range(1,9):
    channel[str(i)+'/power']={
        'valueInit' : 0.,
        'brokerInit' : True,
        'format' : "0:1200",
        'unit': 'uW',
        }
    channel[str(i)+'/frequency']={
        'valueInit' : 0.,
        'brokerInit' : True,
        'format' : "300:900",
        'unit': 'THz',
        }


initNodes = {}
initNodes['config'] = config
initNodes['channel'] = channel
initNodes['main'] = main

class DeviceClass(DeviceBase):
    def init_pre(self):
        self.locks = {}
        self.initNodes = initNodes
        self.wlm = WlmDllCaller()

    def device_thread(self):
        while self.up:
            self.get_all()

    def get_all(self):
        results = self.read_multi(
                [self.wlm.get_frequency, self.wlm.get_power],10)
        results_t = np.array(results).transpose()
        # should we check for finished threads?
        adj_freq = Thread(target=self.adjust_frequencies, args=(results_t,))
        adj_freq.start()
        pub_ch = Thread(target=self.publish_channels, args=(results_t,))
        pub_ch.start()

    def adjust_frequencies(self, results_t):
        for i,name in enumerate(self.locks):
            lock = self.locks[name]
            if lock.active:
                freqNew = (results_t[0][lock.wavemeterchannel-1]).mean()
                lock.adj_freq(freqNew)

    def publish_channels(self, results_t):
        for i in range(8):
            self.params['channel/'+str(i+1)+'/frequency'].publish_value(
                    float(results_t[0][i].mean()))
            self.params['channel/'+str(i+1)+'/power'].publish_value(
                    float(results_t[1][i].mean()))
        self.params['main/temperature'].publish_value(float(self.wlm.get_temperature()))
        self.params['main/pressure'].publish_value(float(self.wlm.get_pressure()))


    def create_lock(self, name):
        if name in self.locks:
            self.dev.log('Lock "'
                    +name
                    +'" already exists.', 30)
        else:
            self.locks[name] = LaserLock(self.dev, name)
            self.locks[name].init_after()
            if 'config/locks' in self.params:
                if not name in self.params['config/locks'].value:
                    self.params['config/locks'].value.append(name)
                    self.params['config/locks'].publish_value()

    def read_all_ch(self, read_functions, values):
        for i,value in enumerate(values):
            for ii,read_function in enumerate(read_functions):
                value.append(read_function(i+1))
        return values

    def read_multi(self, read_functions, reps, waitTime=0.01):
        results = []
        for rep in range(reps):
            values = [[] for i in range(8)]
            self.read_all_ch(read_functions, values)
            results.append(values)
            time.sleep(waitTime)
        return results
