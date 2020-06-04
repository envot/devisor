#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an IoT manner via the MQTT protocol.
# Klemens Schueppert : schueppi@envot.io

import argparse
import time
import os
import sys
import signal

from devisor import DeVisor

parser = argparse.ArgumentParser(description= 'DeVisor: Python program to control, monitor and configure devices in an EoT: https://envot.io')
parser.add_argument('-host', type=str, help='Host of MQTT Broker. STR Default: "localhost"')
parser.add_argument('-port', type=str, help='Port of MQTT Broker. INT Default: 1883')
parser.add_argument('-name', type=str, help='Name of devisor in MQTT. STR Default: Auto read from network device')
args = parser.parse_args()

if args.host == None:
    args.host = "localhost"
if args.port == None:
    args.port = 1883

class Runner:
    run = True
    def __init__(self):
        signal.signal(signal.SIGINT, self.exit)
        signal.signal(signal.SIGTERM, self.exit)

    def exit(self, signum, frame):
        self.run = False


if __name__ == '__main__':
    runner = Runner()
    devisor = DeVisor(host=args.host, port=int(args.port), name=args.name)
    print('Started.')
    while runner.run and devisor.RUN:
        time.sleep(1)
devisor.exit()
if devisor.RUN:
    print("Exiting...")
else:
    print("Restarting DeVisor...")
    os.execl(sys.executable, sys.executable, *sys.argv)
