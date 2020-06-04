#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import socket
import sys
import struct
import random
import time


class Socket4SCPI:
    def __init__(self, host, port=5000, timeout=1, eol='\n', debugmode = False):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.debugmode = debugmode
        if not self.debugmode:
            self.open()
        self.eol = eol
        self.failure = 0
        self.inUse = False

    def raw_send(self, cmd='*IDN?'):
        cmdb = cmd+self.eol
        if self.debugmode:
            print(cmdb)
            return True
        self.socket.send(cmdb.encode())
        return True

    def send(self, cmd='*IDN?'):
        self._check_use()
        cmdb = cmd+self.eol
        if self.debugmode:
            print(cmdb)
        else:
            self.socket.send(cmdb.encode())
        if '?' in cmd:
            result = self.get(cmdb)
            self.inUse = False
            return result
        self.inUse = False
        return True

    def get(self, cmdb=''):
        data = ""
        if self.debugmode:
            data = str(random.randint(0,4))
            return data
        try:
            while (not data.endswith(self.eol)) or data=='\n':
                data += self.socket.recv(1024).decode()
            return data[:-len(self.eol)]
        except Exception:
            # this should be logged
            #err = sys.exc_info()[1]
            self.failure += 1
            if self.failure < 2:
                data = self.send(cmdb)
            elif self.failure < 3:
                self.reconnect()
                data = self.send(cmdb)
            else:
                # log again!
                pass
            return data 
        
    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
        self.socket.settimeout(self.timeout)
        self.inUse = False
        
    def close(self):
        if self.debugmode:
            print('socket closed')
        else:
            self.socket.close()
            del(self.socket)

    def reconnect(self):
        self.close()
        self.open()

    def _check_use(self):
        while self.inUse:
            time.sleep(0.01)
        self.inUse = True

