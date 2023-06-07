#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import time
from threading import Timer

from devisor.devisorbase import DeviceBase
from .api_client import KiutraClient


def rpc_read(pB):
    return pB.dev.query(pB.initDict['cmd'])

def rpc_write(pB):
    pB.dev.query(pB.initDict['cmd, pB.value'])

def rpc_trigger(pB):
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
initNodes['control'] = control

compressor = {}
compressor['status']={
        'valueInit' : False,
        'device_func' : rpc_read,
        'cmd' : 'compressor.runstatus',
        'settable' : False,
        }
compressor['on']={
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : rpc_trigger,
        'cmd' : 'compressor.on',
        'settable' : True,
        }
compressor['off']={
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : rpc_trigger,
        'cmd' : 'compressor.off',
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
        'cmd' : 'T_test1.kelvin',
        'format' : "0:500",
        'settable' : False,
        'unit': 'K',
        }
temperature['test2']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'T_test2.kelvin',
        'format' : "0:500",
        'settable' : False,
        'unit': 'K',
        }
initNodes['temperature'] = temperature

heater = {}
heater['status']={
        'valueInit' : '',
        'device_func' : rpc_read,
        'cmd' : 'warmup_heater.statusinfo',
        'settable' : False,
        }
def rpc_start_heater(pB):
    setpoint = pB.params['heater/setpoint'].value
    ramp = pB.params['heater/ramp'].value
    if pB.value:
        pB.dev.call('warmup_heater.start',(setpoint, ramp))
    pB.publish_value(False)
heater['start']={
        'valueInit' : False,
        'brokerInit' : True,
        'broker_func' : rpc_start_heater,
        'settable' : True,
        'readable' : False,
        }
heater['stop']={
        'valueInit' : False,
        'brokerInit' : True,
        'broker_func' : rpc_trigger,
        'cmd' : 'warmup_heater.stop',
        'settable' : True,
        'readable' : False,
        }
heater['setpoint']={
        'valueInit' : 300.,
        'brokerInit' : True,
        'format' : "0:500",
        'settable' : True,
        'unit': 'K',
        }
heater['ramp']={
        'valueInit' : 0.5,
        'brokerInit' : True,
        'format' : "-1:1",
        'settable' : True,
        'unit': 'K/min',
        }
heater['current']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'warmup_heater.current',
        'format' : "0:50",
        'settable' : True,
        'unit': 'A',
        }
heater['power']={
        'valueInit' : 0.,
        'device_func' : rpc_read,
        'cmd' : 'warmup_heater.power',
        'format' : "0:50",
        'settable' : True,
        'unit': 'W',
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
gashandling['turbopump/start']={
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : rpc_trigger,
        'cmd' : 'turbopump.start',
        'settable' : True,
        }
gashandling['turbopump/stop']={
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : rpc_trigger,
        'cmd' : 'turbopump.stop',
        'settable' : True,
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
gashandling['valves/gate/open']={
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : rpc_trigger,
        'cmd' : 'gate.open',
        'settable' : True,
        'readable' : False,
        }
gashandling['valves/gate/close']={
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : rpc_trigger,
        'cmd' : 'gate.closed',
        'settable' : True,
        'readable' : False,
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
gashandling['valves/main/open']={
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : rpc_trigger,
        'settable' : True,
        'readable' : False,
        'cmd' : 'main.open',
        }
gashandling['valves/main/close']={
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : rpc_trigger,
        'cmd' : 'main.closed',
        'settable' : True,
        'readable' : False,
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
gashandling['valves/utility/open']={
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : rpc_trigger,
        'cmd' : 'utility.open',
        'settable' : True,
        'readable' : False,
        }
gashandling['valves/utility/close']={
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : rpc_trigger,
        'cmd' : 'utility.closed',
        'settable' : True,
        'readable' : False,
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
        self.waittime = 30.
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

    def call(self, cmd, value):
        try:
            self.clientKiutra.call(cmd, value)
        except:
            self.dev.log.new_log('Connection error retry to call"'
                    +cmd+': '+value+'" in '+self.waittime+'s.')
            time.sleep(self.waittime)
            self.call(cmd, value)

    def query(self, cmd):
        try:
            return self.clientKiutra.query(cmd)
        except:
            self.dev.log.new_log('Connection error retry to query"'
                    +cmd+'" in '+str(self.waittime)+'s.')
            time.sleep(self.waittime)
            return self.query(cmd)

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
        data_dict = self.query('compressor.data')
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
