#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
import pyvisa
import sys

class ConnectionClass():
    def __init__(self, devisor, address='USB0::4883::32888::P0031939::0::INSTR'):
        self.devisor = devisor
        self.address = address
        self.addressArray = address.split(',')
        self.fails = 0
        self.open()

    def write(self, value, codec='None'):
        return self.error_handling(self.write, self.instr.write, value)

    def read(self, length=1024, codec='None'):
        return self.error_handling(self.read, self.instr.read, length)

    def ask(self, value, codec='None'):
        return self.error_handling(self.ask, self.instr.query, value)

    def error_handling(self, function, functionInstr, *kwargs):
        try:
            return functionInstr(*kwargs)
        except Exception:
            err = sys.exc_info()[1]
            self.fails += 1
            if self.fails == 1:
                self.devisor.log.new_log('Could not "'+function.__name__+'": '
                    +str(kwargs)+' due to: '+str(err), "INFO")
                self.devisor.log.new_log('Reconnect and try "'+function.__name__
                    +'" again.', "INFO")
                self.reconnect()
                result = function(*kwargs)
                self.fails = 0
                return result
            if self.fails > 1:
                self.devisor.log.new_log('Could not "'+function.__name__+'": '
                    +str(kwargs)+' due to: '+str(err), "WARNING")
                self.fails = 0
                return 0

    def open(self):
        self.rm = pyvisa.ResourceManager()
        self.devisor.log.new_log('Available connections "'
                    +str(self.rm.list_resources())+'"', "INFO")
        try:
            self.instr = self.rm.open_resource(self.addressArray[0])
            self.devisor.log.new_log('Connection "pyvisa" successfully connect to "'
                        +self.addressArray[0]+'"', "INFO")
            return True
        except Exception:
            err = sys.exc_info()[1]
            self.devisor.log.new_log('Could not connect to: '
                    +str(self.addressArray[0])+' due to: '+str(err), "WARNING")
            return False

    def close(self):
        self.instr.close()

    def reconnect(self):
        self.close()
        self.open()
