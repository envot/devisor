#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

from . import mqttlog, connections

class DeVisorDummy():
    """
    Dummy class to fake devisor
    """
    def __init__(self, device_name, host, port):
        self.log = mqttlog.MQTTLog(self)
        self.runningConnections = connections.Connections(self)
        self.host = host
        self.port = port
        self.name = device_name
        self.ip = device_name.split('-')[0]
