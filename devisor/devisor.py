#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io


import time
import datetime
import socket
import os
import sys
import requests

from .devisorbase import DeviceBase,devisor_import
from .connections import Connections

def get_hostname():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    print("Found primary IP : "+str(ip))
    try:
        hostname = socket.gethostbyaddr(ip)[0]
    except:
        hostname = socket.gethostname()
    print("Found hostname: "+str(hostname))
    return ip,hostname

def make_homie_name(rawName):
    name = rawName.translate({ord(c): "-" for c in "!@#$%^&*()[]{};:,./<>?\|`~=_+"})
    while name[0] == '-':
        name = name[1:]
        if name == '':
            name = 'only-special-chars'
    return name.lower()

def list_local_device_packages(availableDevices):
    devisorDevDir = './devisor/devices'
    filenames = os.listdir(devisorDevDir)
    for filename in filenames:
        if (not (filename in ['__pycache__.py'] and
                filename in availableDevices) and
                os.path.isfile(os.path.join(devisorDevDir,filename,'__init__.py'))):
            availableDevices.append(filename)
    return availableDevices

def list_remote_device_packages(availableDevices):
    packages = []
    page = 1
    try:
        while page > 0:
            r = requests.get("https://gitlab.com/api/v4/projects/19185895/packages?per_page=100&page="+str(page))
            if len(r.json()) > 0:
                packages.extend(r.json())
                page += 1
            else:
                page = -1
    except:
        print('No connection to package registry available.')
        return availableDevices
    for package in packages:
        if (not (package['name'][7:] in availableDevices)
                and package['name'][:6] == 'device'
                and package['package_type'] == 'pypi'):
            availableDevices.append(package['name'][7:])
    return availableDevices

availableDevices = []
availableDevices = list_local_device_packages(availableDevices)
availableDevices = list_remote_device_packages(availableDevices)


initNodes = {}
devices = {}

devices['stop/select'] = {
    'valueInit' : '',
    'format' : [],
    'datatype' : 'enum',
    'settable' : True,
    }

def stop_device(pB, topicFolder):
    pB.dev.runningDevices[topicFolder].exit()
    del(pB.dev.runningDevices[topicFolder])
    del(pB.dev.params['devices/running'].value[topicFolder])
    pB.dev.params['devices/running'].publish_value()
    pB.dev.params['devices/stop/select/$format'].value = list(
            pB.dev.params['devices/running'].value.keys())
    pB.dev.params['devices/stop/select/$format'].publish_value()

def start_new_device(pB, topicFolder, address):
    pB.dev.log.new_log('Try to load device "'
                +topicFolder+'" at "'
                +address+'"')
    errorMsg = ''
    className = topicFolder.split('/')[0]
    driver = devisor_import(pB.devisor, className, 'device')
    pB.dev.runningDevices[topicFolder] = driver.DeviceClass(pB.dev, topicFolder, address)
    pB.dev.log.new_log('Initialized device: ' + topicFolder, 'CRITICAL')
    if pB.param == 'devices/running':
        pB.value[topicFolder] = address
        pB.publish_value()
        pB.dev.params['devices/stop/select/$format'].value = list(
            pB.value.keys())
    else:
        pB.dev.params['devices/running'].value[topicFolder] = address
        pB.dev.params['devices/running'].publish_value()
        pB.dev.params['devices/stop/select/$format'].value = list(
            pB.dev.params['devices/running'].value.keys())
    pB.dev.params['devices/stop/select/$format'].publish_value()
    pB.dev.check_name('')
    return True

def handle_devicesRunning(pB):
    devicesToDelete = []
    for topicFolder in pB.value:
        if topicFolder in pB.dev.runningDevices:
            try:
                if pB.dev.runningDevices[topicFolder].params['$state'].value in ['disconnected', 'lost']:
                    pB.dev.runningDevices[topicFolder].exit()
                    raise Exception('Device "'+topicFolder+'" is disconnected or lost')
            except Exception:
                err = sys.exc_info()[1]
                pB.dev.log.new_log(topicFolder+" is listed to be removed due to: "+str(err))
                devicesToDelete.append(topicFolder)
        else:
            start_new_device(pB, topicFolder, pB.value[topicFolder])
    for val in devicesToDelete[::-1]:
        pB.dev.log.new_log(val+' is not running, so it will be removed.', 'CRITICAL')
        del(pB.value[val])
    devicesToDelete = []
    for topicFolder in pB.dev.runningDevices:
        if not topicFolder in pB.value:
            devicesToDelete.append(topicFolder)
    for topicFolder in devicesToDelete[::-1]:
        pB.dev.log.new_log('We close '+topicFolder+'.')
        pB.dev.runningDevices[topicFolder].exit()
        del(pB.dev.runningDevices[topicFolder])
    pB.dev.params['devices/stop/select/$format'].value = list(
            pB.value.keys())
    pB.dev.params['devices/stop/select/$format'].publish_value()

devices['running'] = {
    'valueInit' : {},
    'broker_func' : handle_devicesRunning,
    'brokerInit' : True,
    'settable' : True,
}

devices['start/type'] = {
    'valueInit' : 'testdevice',
    'format' : availableDevices,
    'datatype' : 'enum',
    'settable' : True,
    'brokerInit' : True,
    }

devices['start/name'] = {
    'valueInit' : 'newname',
    'settable' : True,
    'brokerInit' : True,
    }

devices['start/address'] = {
    'valueInit' : 'persistent',
    'settable' : True,
    'brokerInit' : True,
    }


def handle_deviceStartSwitch(pB):
    topicFolder = '/'.join([pB.dev.params['devices/start/type'].value,
                            pB.dev.params['devices/start/name'].value])
    if topicFolder in pB.dev.runningDevices:
        pB.dev.log.new_log('Device "'+
                topicFolder+'" is already running.')
    else:
        start_new_device(pB, topicFolder, pB.dev.params['devices/start/address'].value)
    pB.value = False
    pB.publish_value()

devices['start'] = {
    'valueInit' : False,
    'broker_func' : handle_deviceStartSwitch,
    'settable' : True,
}


def handle_deviceStopSwitch(pB):
    topicFolder = pB.dev.params['devices/stop/select'].value
    if topicFolder in pB.dev.runningDevices:
        stop_device(pB, topicFolder)
        pB.dev.log.new_log('Device "'+
                topicFolder+'" stopped.', 'CRITICAL')
    else:
        pB.dev.log.new_log('Device "'+
                topicFolder+'" is not running.')
    pB.value = False
    pB.publish_value()

devices['stop'] = {
    'valueInit' : False,
    'broker_func' : handle_deviceStopSwitch,
    'settable' : True,
}


order = list(devices.keys())
order.remove('running')
order.remove('start/name')
order.remove('stop/select')
order.append('start/name')
order.append('running')
order.insert(0, 'stop/select')
devices['order'] = order
initNodes['devices'] = devices


control = {}

def reboot_devisor(pB):
    pB.valueOld = pB.value
    pB.value = False
    pB.publish_value()
    if pB.valueOld:
        print('Rebooting...')
        pB.dev.RUN = False

control['reboot'] = {
    'valueInit' : False,
    'broker_func' : reboot_devisor,
    'settable' : True,
}

def refresh_devisor(pB):
    pB.valueOld = pB.value
    pB.value = False
    pB.publish_value()
    if pB.valueOld:
        pB.dev.log.new_log('Refreshing values ...')
        pB.dev.publish_all_devices(attributes=False)
        pB.dev.log.new_log('...Refreshed')

control['refresh'] = {
    'valueInit' : False,
    'broker_func' : refresh_devisor,
    'settable' : True,
}


def upgrade_devisor(pB):
    pB.valueOld = pB.value
    if pB.valueOld:
        pB.dev.log.new_log('Pulling git...')
        pB.dev.log.new_log(os.popen('git pull').read())
    pB.value = False
    pB.publish_value()

control['upgrade'] = {
    'valueInit' : False,
    'broker_func' : upgrade_devisor,
    'settable' : True,
}

initNodes['control'] = control



class DeVisor(DeviceBase):
    def __init__(self, host, port, name=None):
        self.host = host
        self.port = port
        self.ip,ipname = get_hostname()
        self.address = self.ip
        if name == None:
            name = ipname
        self.name = make_homie_name(name)
        self.devisor = self
        self.dev = self
        self.topicFolder = ("devisor/"+self.name)
        self.runningConnections = Connections(self)
        self.runningDevices = {}
        self.subscribed = []

        self.init_basics()

        self.otherDevices = {}
        self.client.subscribe('+/+/$state')

        self.initNodes = initNodes
        self.init_standards()
        self.params['devices/start/type'].broker_func = self.check_name
        self.params['devices/start/name'].broker_func = self.check_name
        self.check_name('')
        self.RUN = True

    def publish_all_devices(self, attributes=False):
        self.publish_all(attributes)
        for dev in self.runningDevices:
            self.runningDevices[dev].publish_all(attributes)
        
    def exit_pre(self):
        self.client.unsubscribe('+/+/$state')
        for deviceName in self.runningDevices:
            topicFolder = self.runningDevices[deviceName].topicFolder
            self.runningDevices[topicFolder].exit()

    def check_name(self, topicMessage):
        newName = self.params['devices/start/name']
        newName.valueOld = newName.value
        newName.value = make_homie_name(newName.value)
        for device in self.otherDevices.keys():
            deviceArr = device.split('/')
            if newName.value == deviceArr[1]:
                if self.otherDevices[device] in ['ready', 'init']:
                    self.log.new_log('Device "' + device
                            + '" is already running -> New device name is changed...', 'WARNING')
                    newName.value += '2'
                    self.check_name('')
                    break
                else:
                    if not self.params['devices/start/type'].value == deviceArr[0]:
                        self.log.new_log('Device "' + device
                                + '" already exists -> New device name must be different due to Homie convention: unique device ID.', 'WARNING')
                        newName.value += '2'
                        self.check_name('')
                        break
                    else:
                        self.log.new_log('Device "'+device
                            + '" already exists and can be restarted.', 'INFO')
        newName.publish_value()

    def otherMessage(self, topicFolder, topicName, payload):
        if topicName in ['$state']:
            if payload == '':
                del(self.otherDevices[topicFolder])
            else:
                self.otherDevices[topicFolder] = payload
                self.check_name('')
