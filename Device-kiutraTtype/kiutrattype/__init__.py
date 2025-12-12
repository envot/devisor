#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time
from threading import Timer

from devisor.devisorbase import DeviceBase
from .api_client import KiutraClient


def rpc_read(pB):
    return pB.dev.query_value(pB.initDict['cmd'])

def rpc_set(pB):
    pB.dev.set_value(pB.initDict['cmd'], pB.value)

def rpc_call(pB):
    pB.dev.call(pB.initDict['cmd'], pB.value)

def rpc_call_trigger(pB):
    if pB.value:
        pB.dev.call(pB.initDict['cmd'])
        pB.publish_value(False)

initNodes = {}
config = {}
def control_change_read_interval(pB):
    if pB.dev.up:
        if pB.dev.ReadOutThread.is_alive():
            pB.dev.ReadOutThread.cancel()
        pB.dev.device_thread()
config['refresh-interval']={
    'valueInit' : 5.,
    'brokerInit' : True,
    'broker_func' : control_change_read_interval,
    'format' : "1:10000",
    'settable' : True,
    'unit': 's',
}
initNodes['config'] = config

control = {}
control['status']={
        'valueInit' : '',
        'device_func' : rpc_read,
        'cmd' : 'cryostat.runstatus',
        'settable' : False,
        }
control['statusinfo']={
        'valueInit' : '',
        'device_func' : rpc_read,
        'cmd' : 'cryostat.status',
        'settable' : False,
        }
control['reset']={
        'valueInit' : False,
        'broker_func' : rpc_call_trigger,
        'cmd' : 'cryostat.reset',
        'settable' : True,
        }
control['blocking-devices']={
        'valueInit' : [],
        'device_func' : rpc_read,
        'cmd' : 'cryostat.blocking_devices',
        'settable' : False,
        }
control['blocked']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'cmd' : 'cryostat.is_blocked',
        'settable' : False,
        }
control['cooling-rate']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'cryostat.temperature_rate',
        'format' : "-100:100",
        'settable' : False,
        'unit': 'K/min',
        }
control['progress']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'cryostat.display_progress',
        'format' : "0:100",
        'settable' : False,
        'unit': 'K/min',
        }
control['process-step']={
        'valueInit' : '',
        'device_func' : rpc_read,
        'cmd' : 'cryostat.detailed_progress',
        'settable' : False,
        }
control['warmup-setpoint']={
        'valueInit' : 300.,
        'device_func' : rpc_read,
        'broker_func' : rpc_set,
        'brokerInit' : True,
        'format' : "0:310",
        'settable' : True,
        'cmd' : 'cryostat.warmup_setpoint',
        'unit': 'K',
        }
control['warmup-ramp']={
        'valueInit' : 1.0,
        #'device_func' : rpc_read,
        'broker_func' : rpc_set,
        'brokerInit' : True,
        'format' : "-1:1",
        'settable' : True,
        'cmd' : 'cryostat.warmup_ramp',
        'unit': 'K/min',
        }
control['soft-cooldown-temperature']={
        'valueInit' : 150.,
        'device_func' : rpc_read,
        'broker_func' : rpc_set,
        'brokerInit' : True,
        'format' : "100:280",
        'settable' : True,
        'cmd' : 'cryostat.soft_cooldown_temperature',
        'unit': 'K',
        }
control['program-select']={
        'valueInit' : 'soft_cooldown',
        'brokerInit' : True,
        'settable' : True,
        'readable' : False,
        'format' : ['cooldown', 'soft_cooldown', 'warmup', 'prepare_purge', 'purge pulse', 'stop_purge', 'warmup_purge', 'return_to_idle', 'initialize', 'evacuate', 'pump_and_heat', 'vent', 'purge_dewar', 'brake_pumps', 'stop_pumps', 'open_gate', 'close_gate', 'check_purge', 'stop_heater', 'start_heater'],
        }
def program_start(pB):
    if pB.value:
        pB.dev.call('cryostat.start', pB.dev.params['control/program-select'].value)
        pB.publish_value(False)
control['program-start']={
        'valueInit' : False,
        'broker_func' : program_start,
        'settable' : True,
        'readable' : False,
        }
def program_stop(pB):
    if pB.value:
        pB.dev.call('cryostat.stop')
        pB.value=False
control['program-stop']={
        'valueInit' : False,
        'broker_func' : program_stop,
        'settable' : True,
        'readable' : False,
        }
initNodes['control'] = control

compressor = {}
compressor['status']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'cmd' : 'compressor.runstatus',
        'settable' : False,
        }
compressor['reset']={
        'valueInit' : False,
        'broker_func' : rpc_call_trigger,
        'cmd' : 'compressor.reset',
        'settable' : True,
        }
compressor['pressure']={
        'valueInit' : 0.,
        'brokerInit' : True,
        'format' : "0:30",
        'settable' : False,
        'unit': 'bar',
        }
compressor['operation-hours']={
        'valueInit' : 0.,
        'brokerInit' : True,
        'cmd' : 'compressor.operating_hours',
        'format' : "0:1000000",
        'settable' : False,
        'unit': 'h',
        }
compressor['error/gas-flow']={
        'valueInit' : False,
        'brokerInit' : True,
        'settable' : False,
        }
compressor['error/gas-temperature']={
        'valueInit' : False,
        'brokerInit' : True,
        'settable' : False,
        }
compressor['error/motor-temperature']={
        'valueInit' : False,
        'brokerInit' : True,
        'settable' : False,
        }
compressor['error/power']={
        'valueInit' : False,
        'brokerInit' : True,
        'settable' : False,
        }
compressor['error/water-temperature']={
        'valueInit' : False,
        'brokerInit' : True,
        'settable' : False,
        }
compressor['error/water-flow']={
        'valueInit' : False,
        'brokerInit' : True,
        'settable' : False,
        }
compressor['error/water']={
        'valueInit' : False,
        'brokerInit' : True,
        'settable' : False,
        }
initNodes['compressor'] = compressor

temperature = {}
temperature['ccr1']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'T_ccr1.kelvin',
        'format' : "0:500",
        'settable' : False,
        'unit': 'K',
        }
temperature['ccr2']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'T_ccr2.kelvin',
        'format' : "0:500",
        'settable' : False,
        'unit': 'K',
        }
temperature['test1']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'T_test1.sensorunits',
        'settable' : False,
        }
temperature['test2']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'T_test2.sensorunits',
        'settable' : False,
        }
initNodes['temperature'] = temperature

heater = {}
def start_sample_heater(pB):
    if pB.dev.up:
        pB.dev.call('sample_heater.start', (
            pB.dev.params['heater/sample/setpoint'].value,
            pB.dev.params['heater/sample/rate'].value))
def trigger_heater_sample_start(pB):
    if pB.value and pB.dev.up:
        start_sample_heater(pB)
        pB.value=False
heater['sample/status']={
        'valueInit' : '',
        'device_func' : rpc_read,
        'cmd' : 'sample_heater.status',
        'settable' : False,
        }
heater['sample/reset']={
        'valueInit' : False,
        'broker_func' : rpc_call_trigger,
        'cmd' : 'sample_heater.reset',
        'settable' : True,
        }
heater['sample/setpoint']={
        'valueInit' : 300.,
        'device_func' : rpc_read,
        'broker_func' : rpc_set,
        'brokerInit' : True,
        'format' : "0:315",
        'settable' : True,
        'cmd' : 'sample_heater.setpoint',
        'unit': 'K',
        }
heater['sample/rate']={
        'valueInit' : 0.5,
        'broker_func' : start_sample_heater,
        'brokerInit' : True,
        'format' : "-1:1",
        'settable' : True,
        'readable': True,
        'cmd' : 'sample_heater.rate',
        'unit': 'K/min',
        }
heater['sample/power']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'sample_heater.power',
        'format' : "0:50",
        'settable' : True,
        'unit': 'W',
        }
heater['sample/start']={
        'valueInit' : False,
        'device_func' : trigger_heater_sample_start,
        'cmd' : 'sample_heater.start',
        'settable' : True,
        }
heater['sample/stop']={
        'valueInit' : False,
        'device_func' : rpc_call_trigger,
        'cmd' : 'sample_heater.stop',
        'settable' : True,
        }
def start_warmup_heater(pB):
    if pB.dev.up:
        pB.dev.call('warmup_heater.start', (
            pB.dev.params['heater/warmup/setpoint'].value,
            pB.dev.params['heater/warmup/rate'].value))
def trigger_heater_warmup_start(pB):
    if pB.value and pB.dev.up:
        start_warmup_heater(pB)
        pB.value=False
heater['warmup/status']={
        'valueInit' : '',
        'device_func' : rpc_read,
        'cmd' : 'warmup_heater.status',
        'settable' : False,
        }
heater['warmup/reset']={
        'valueInit' : False,
        'broker_func' : rpc_call_trigger,
        'cmd' : 'ccr1_heater.reset',
        'settable' : True,
        }
heater['warmup/setpoint']={
        'valueInit' : 300.,
        'device_func' : rpc_read,
        'broker_func' : rpc_set,
        'brokerInit' : True,
        'format' : "0:315",
        'settable' : True,
        'cmd' : 'ccr1_heater.setpoint',
        'unit': 'K',
        }
heater['warmup/rate']={
        'valueInit' : 1.0,
        'broker_func' : start_warmup_heater,
        'brokerInit' : True,
        'format' : "-1:1",
        'settable' : True,
        'readable': True,
        'cmd' : 'ccr1_heater.rate',
        'unit': 'K/min',
        }
heater['warmup/power']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'ccr1_heater.power',
        'format' : "0:50",
        'settable' : True,
        'unit': 'W',
        }
heater['warmup/start']={
        'valueInit' : False,
        'device_func' : trigger_heater_warmup_start,
        'cmd' : 'ccr1_heater.start',
        'settable' : True,
        }
heater['warmup/stop']={
        'valueInit' : False,
        'device_func' : rpc_call_trigger,
        'cmd' : 'ccr1_heater.stop',
        'settable' : True,
        }
initNodes['heater'] = heater

gashandling = {}
gashandling['pressure']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'isovac.pressure',
        'format' : "0:1200",
        'settable' : False,
        'unit': 'mbar',
        }

gashandling['forepump/status']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'cmd' : 'forepump.is_on',
        'settable' : False,
        }

gashandling['turbopump/status']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'settable' : False,
        'cmd' : 'turbopump.is_on',
        }
gashandling['turbopump/speed']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'turbopump.frequency',
        'format' : "0:12000",
        'settable' : False,
        'unit': 'Hz',
        }
gashandling['turbopump/temperature']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'turbopump.temperature',
        'format' : "0:10",
        'settable' : False,
        'unit': 'A',
        }
gashandling['turbopump/current']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'turbopump.current',
        'format' : "0:10",
        'settable' : False,
        'unit': 'A',
        }
gashandling['turbopump/operation-counter']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'turbopump.operation_counter',
        'format' : "0:1000",
        'settable' : False,
        }
gashandling['turbopump/operation-hours']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'turbopump.operation_hours',
        'format' : "0:100000",
        'settable' : False,
        'unit': 'h',
        }

gashandling['valves/gate/opened']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'cmd' : 'gate.is_open',
        'settable' : False,
        }
gashandling['valves/gate/closed']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'cmd' : 'gate.is_closed',
        'settable' : False,
        }

gashandling['valves/main/opened']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'cmd' : 'main.is_open',
        'settable' : False,
        }
gashandling['valves/main/closed']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'cmd' : 'main.is_closed',
        'settable' : False,
        }
gashandling['valves/utility/opened']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'cmd' : 'utility.is_open',
        'settable' : False,
        }

gashandling['valves/utility/closed']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'settable' : False,
        'cmd' : 'utility.is_closed',
        }
gashandling['gas/air']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'compressed_air.pressure',
        'format' : "0:10",
        'settable' : False,
        'unit': 'bar',
        }
gashandling['gas/purge']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'purge_gas.pressure',
        'format' : "-10:10",
        'settable' : False,
        'unit': 'bar',
        }
initNodes['gashandling'] = gashandling


class DeviceClass(DeviceBase):
    def init_pre(self):
        self.waittime = 3.
        self.initNodes = initNodes
        self.initedNodes = initNodes
        addressArray = self.address.split(':')
        self.host = addressArray[0]
        if len(addressArray) > 1:
            self.port = int(addressArray[1])
        else:
            self.port = 1006
        self.clientKiutra = KiutraClient(self.host, port=self.port)

    def device_thread(self, waitTime=1.):
        self.ReadOutThread = Timer(waitTime, self.get_all)
        self.ReadOutThread.start()

    def call(self, cmd, *args, rep=0, **kwargs):
        try:
            self.clientKiutra.call(cmd, *args, **kwargs)
        except:
            self.dev.log.new_log('Connection error: Retry to call "'
                    +str(cmd)+'" in '+str(self.waittime)+'s.')
            time.sleep(self.waittime)
            rep+=1
            if rep < 3:
                self.call(cmd, *args, rep=rep, **kwargs)
            else:
                self.dev.log.new_log('Connection not worked after 3 retries "'
                    +cmd+'" in '+str(self.waittime)+'s.')
                return False

    def query_value(self, cmd, rep=0):
        try:
            return self.clientKiutra.query(cmd)
        except:
            self.dev.log.new_log('Connection error: Retry to query "'
                    +cmd+'" in '+str(self.waittime)+'s.')
            time.sleep(self.waittime)
            rep+=1
            if rep < 3:
                return self.query_value(cmd, rep=rep)
            else:
                self.dev.log.new_log('Connection not worked after 3 retries "'
                    +cmd+'" in '+str(self.waittime)+'s.')
                return False

    def set_value(self, cmd, value, rep=0):
        try:
            return self.clientKiutra.set(cmd, value)
        except:
            self.dev.log.new_log('Connection error: Retry to set"'
                    +cmd+'" in '+str(self.waittime)+'s.')
            time.sleep(self.waittime)
            rep+=1
            if rep < 3:
                return self.set_value(cmd, value, rep=rep)
            else:
                self.dev.log.new_log('Connection not worked after 3 retries'
                    +cmd+'" in '+str(self.waittime)+'s.')
                return False

    def get_all(self):
        starttime = time.time()
        self.read_compressor()
        for node in self.initedNodes:
            for param in self.initedNodes[node]:
                if 'device_func' in self.initedNodes[node][param]:
                    self.params[node+'/'+param].device()
        self.device_thread(max(0,
                self.params['config/refresh-interval'].value)-time.time()+starttime)

    def read_compressor(self):
        data_dict = self.query_value('compressor.data')
        if type(data_dict) != type(None):
            self.params['compressor/status'].publish_value(data_dict['runstatus'])
            self.params['compressor/error/water-flow'].publish_value(data_dict['waterflow_error'])
            self.params['compressor/error/water-temperature'].publish_value(data_dict['watertemp_error'])
            self.params['compressor/error/water'].publish_value(data_dict['water_warning'])
            self.params['compressor/error/motor-temperature'].publish_value(data_dict['motortemp_error'])
            self.params['compressor/error/gas-temperature'].publish_value(data_dict['gastemp_error'])
            self.params['compressor/error/gas-flow'].publish_value(data_dict['gasflow_error'])
            self.params['compressor/error/power'].publish_value(data_dict['power_error'])
            self.params['compressor/pressure'].publish_value(data_dict['return_pressure'])
            self.params['compressor/operation-hours'].publish_value(data_dict['operating_hours'])

    def exit_pre(self):
        self.ReadOutThread.cancel()
