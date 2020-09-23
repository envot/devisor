#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import datetime

from .params import initLogging


LOG_LEVELS = {
        'CRITICAL' : 50,
        'ERROR' : 40,
        'WARNING' : 30,
        'INFO' : 20,
        'DEBUG' : 10,
        }

class MQTTLog():
    def __init__(self, dev):
        self.dev = dev
        self.logArray = []
        self.length = 1000
        self.level = 0
        self.new_log('Initialized log')

    def init_mqtt(self):
        self.dev.initNodes = initLogging
        self.dev._init_nodes()
        self.new_log('Log via MQTT is initialized.')

    def new_log(self, logMessage, level='INFO'):
        if self._convert_level(level) >= self.level:
            logMessageTimed = str(datetime.datetime.now())[:-4]+': '+logMessage

            self.logArray.append(logMessageTimed)
            self.logArray = self.logArray[-self.length:]
            try:
                self.dev.params['logging/logs'].device('\r\n'.join(self.logArray))
            except:
                pass
        
    def change_level(self, level):
        newlevel = self._convert_level(level)
        if newlevel:
            self.level = newlevel
            self.new_log('Changed log level to '+str(level)+'.', 'CRITICAL')
        else:
            self.new_log('Log level change failed.', 'CRITICAL')

    def _convert_level(self, level):
        errorMsg = ''
        if type(level) == int:
            return level
        elif type(level) == str:
            if level in LOG_LEVELS:
                return LOG_LEVELS[level.upper()]
            else:
                errorMsg = 'Log level "'+level+'"not available.'
        else:
            errorMsg = 'Log level type "'+type(level)+'" not known.'
        if errorMsg:
            self.new_log("Log level recognization failed: "+errorMsg, level='DEBUG')
        return False

