#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import json
import time
import traceback

import _thread

BROKER_TRUE='true'
BROKER_FALSE='false'
LIST_SEPARATOR=','

def init_param_property(dev, param, initDict):
    paramType = type(initDict['valueInit'])
    if paramType == bool:
        newClass = ParameterProcessor_bool(dev, param, initDict)
    elif paramType == int:
        newClass = ParameterProcessor_int(dev, param, initDict)
    elif paramType == float:
        newClass = ParameterProcessor_float(dev, param, initDict)
    elif paramType == list:
        initDict['valueInit'] = initDict['valueInit'].copy()
        newClass = ParameterProcessor_list(dev, param, initDict)
    elif paramType == dict:
        initDict['valueInit'] = initDict['valueInit'].copy()
        newClass = ParameterProcessor_dict(dev, param, initDict)
    else:
        newClass = ParameterProcessor(dev, param, initDict)
    dev.params[param] = newClass 



class ParameterProcessor():
    def __init__(self, dev, param, initDict):
        self.dev = dev
        self.devisor = dev.devisor
        self.param = param
        self.name = param.split('/')[-1]
        self.initDict = initDict
        self.valueInit = initDict['valueInit']
        self.value = self.valueInit
        self.type = type(initDict['valueInit'])
        self.valueOld = self.value
        self.triggerParams = []
        self.payload = self.convert_value()
        self.payloadOld = self.convert_value()

        if 'variables' in initDict:
            self.variables = initDict['variables']

        if 'device_func' in initDict:
            self.device_func = initDict['device_func']

        if 'broker_func' in initDict:
            self.broker_func = initDict['broker_func']
        if 'brokerInit' in initDict:
            if initDict['brokerInit']:
                if self.param in self.dev.initBrokerMsgs:
                    self.broker(self.dev.initBrokerMsgs[param])
            else:
                self.device(self.valueInit)
        else:
            self.device(self.valueInit)

    def broker(self, payload):
        if payload == self.payload:
            return True
        self.payload = payload
        newValue = self.convert_payload()
        self.payloadOld = self.payload
        self.valueOld = self.value
        self.value = newValue 
        self.broker_func(self)
        self.trigger_value_change()

    def broker_func(self, dummy):
        pass


    def device(self, value):
        self.valueOld = self.value
        self.value = value
        self.device_func(self)
        self.trigger_value_change()

    def device_func(self, dummy):
        pass


    def convert_payload(self):
        try:
            return self._convert_payload()
        except:
            self.new_log(traceback.format_exc(), 'CRITICAL')
            return self.valueInit

    def _convert_payload(self):
        return self.type(self.payload)

    def convert_value(self):
        return str(self.value)

    def publish_value(self):
        self.payload = self.convert_value()
        self.dev.publish_topic(self.param, self.payload)
        return True

    def close(self):
        self.dev.remove_topic(self.param)

    def new_log(self, logStr, level='DEBUG'):
        self.dev.log.new_log(self.param+': '+logStr, level)

    def trigger_value_change(self):
        self.publish_value()
        for triggerParam in self.triggerParams:
            self.dev.params[triggerParam].device(self.value)



class ParameterProcessor_bool(ParameterProcessor):
    def _convert_payload(self):
        if self.payload == BROKER_TRUE:
            return True
        if self.payload == BROKER_FALSE:
            return False

    def convert_value(self):
        if self.value:
            return BROKER_TRUE
        if not self.value:
            return BROKER_FALSE


class ParameterProcessor_int(ParameterProcessor):
    def _convert_payload(self):
        return int(float(self.payload))

    def convert_value(self):
        return str(self.value)


class ParameterProcessor_float(ParameterProcessor):
    def _convert_payload(self):
        return float(self.payload)

    def convert_value(self):
        return str(self.value)


class ParameterProcessor_list(ParameterProcessor):
    def _convert_payload(self):
        return self.payload.split(LIST_SEPARATOR)
    
    def convert_value(self):
        return LIST_SEPARATOR.join(self.value)


class ParameterProcessor_dict(ParameterProcessor):
    def _convert_payload(self):
        return json.loads(self.payload)
    
    def convert_value(self):
        return json.dumps(self.value, sort_keys=True)
