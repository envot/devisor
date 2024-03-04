#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Jakob Wahl : jakob.wahl@infineon.com
# Klemens Schueppert : schueppi@envot.io

import time
import telnetlib

class ConnectionClass():
    def __init__(self, devisor, address='localhost:23'):
        self.host = address.split(':')[0]
        self.port = int(address.split(':')[1])
        self.devisor = devisor 
        self.eol = b'\r\n'
        # connection timeout 
        self.timeout = 1
        self._connect_device()
        self.block = False


    def _wait_ready(func):
        '''
        Decorator, that makes function wait until self.block=False. 
        Then blocks, and at the end unblock.
        '''
        def inner(self, *args, **kwargs):
            while self.block:
                time.sleep(0.01)
            self.block = True
            result = func(self, *args, **kwargs)
            self.block = False
            return result
        return inner


    def _connect_device(self):
        '''
        Establish connection.
        '''
        self.t = telnetlib.Telnet(self.host, port=self.port)
        self.devisor.log.new_log('Established "telnet" connection.', 'INFO')


    @_wait_ready
    def write(self, value):
        '''
        Writes value to telnet device. Does not expect an answer.
        '''
        attempts = 0 
        success = False
        while attempts < 3 and not success:
            attempts += 1
            try:
                self.t.write(value.encode() + self.eol)
                success = True
            except (EOFError, BrokenPipeError) as e:
                self.devisor.log.new_log('Connection "telnet" timed out. Attempt reconnection..', 'INFO')
                self._connect_device()
            except Exception as e:
                self.devisor.log.new_log('Connection "telnet" failed to write "'
                        + value +'". Function exited with error:\n' + repr(e), "ERROR")
                break

        if not success:
            self.devisor.log.new_log('Connection "telnet" broke. Reconnection failed 3 times.', "ERROR")


    @_wait_ready
    def ask(self, question):
        '''
        Send a question and wait for one of the given possible answers.
        '''
        attempts = 0 
        success = False
        while attempts < 3 and not success:
            attempts += 1
            try:
                self.t.write(question.encode() + self.eol)
                success = True
            except (EOFError, BrokenPipeError) as e:
                self.devisor.log.new_log('Connection "telnet" timed out. Attempt reconnection..', 'INFO')
                self._connect_device()
            except Exception as e:
                self.devisor.log.new_log('Connection "telnet" failed to ask "'
                        + question +'". Function exited with error:\n' + repr(e), "ERROR")
                return ""
                
        if not success:
            self.devisor.log.new_log('Connection "telnet" broke. Reconnection failed 3 times.', "ERROR")
            return ""

        return self.t.read_until(self.eol).decode().strip("\r\n")