#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Python program to control, monitor and configure devices in an IoT manner via the MQTT protocol.
# Klemens Schueppert : schueppi@envot.io

import argparse
import time
import os
import sys
import signal

from devisor.devisor import DeVisor, get_hostname, make_homie_name
from devisor.devisorbase import devisor_import
from devisor.connections import Connections

parser = argparse.ArgumentParser(description=
    'DeVisor: Python program to control, monitor and configure devices in an EoT: https://envot.io')
parser.add_argument('-host', type=str, help=
    'Host of MQTT Broker. STR Default: "localhost"')
parser.add_argument('-port', type=str, help=
    'Port of MQTT Broker. INT Default: 1883')
parser.add_argument('-name', type=str, help=
    'Name of devisor or device (if -device given) in MQTT.'
        +' STR Default: Auto read from network device')
parser.add_argument('-device', type=str, help=
    'Type of device to start directly without devisor.'
        +' Parameter name is device name.'
        +' STR Default: None -> start devisor')
parser.add_argument ('-address', type=str, help=
    'Address of device to start directly a device at given address.'
        +' STR Default: None -> try to start device from MQTT info')
args = parser.parse_args()

if args.host is None:
    args.host = "localhost"
if args.port is None:
    args.port = 1883

ip,ipname = get_hostname()
if args.name is None:
    args.name = ipname
name = make_homie_name(args.name)

class DeVisorDummy:
    def __init__(self):
        self.runningConnections = Connections(self)
        self.host = args.host
        self.port = args.port
        self.name = args.name
        self.ip = ip
dev = DeVisorDummy()

class Runner:
    run = True
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, signum, frame):
        self.run = False


if __name__ == '__main__':
    runner = Runner()
    if args.device is None:
        devisor = DeVisor(host=args.host, port=int(args.port), name=name)
        print('Devisor ' + name + ' started.')
    else:
        driver = devisor_import(None, args.device, 'device')
        devisor = driver.DeviceClass(dev, args.device+'/'+name,
                args.address, ip=ip, host=args.host, port=args.port)
        print(args.device + ' ' + args.name + ' started @ ' + str(args.address) + '.')
    while runner.run and devisor.RUN:
        time.sleep(1)
devisor.exit()
if devisor.RUN:
    print("Exiting...")
else:
    print("Restarting DeVisor...")
    os.execl(sys.executable, sys.executable, *sys.argv)
