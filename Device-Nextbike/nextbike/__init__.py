#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

import requests
import time

from devisor.devisorbase import DeviceBase


def create_station(pB):
    uid = pB.dev.params['config/station-uid'].value
    name = pB.dev.params['config/station-name'].value
    pB.dev.create_station(uid, name)
    pB.device(False)

def handle_stations(pB):
    stations2del = []
    for startedStationUID in pB.dev.stations:
        if not startedStationUID in pB.value:
            stations2del.append(startedStationUID)
    for station2del in stations2del:
        pB.dev.log.new_log('We close '+station2del+'.')
        del(pB.dev.stationsName[pB.dev.stations[station2del].name])
        pB.dev.stations[station2del].exit()
        del(pB.dev.stations[station2del])
    for stationUID in pB.value:
        if not stationUID in pB.dev.stations:
            pB.dev.create_station(stationUID, pB.value[stationUID])
            pB.dev.stationsName[pB.dev.stations[stationUID].name] = stationUID


initNodes = {}

config = {}
config['station-name']={
    'valueInit' : '',
    'brokerInit' : True,
    'settable' : True,
}
config['station-uid']={
    'valueInit' : '',
    'brokerInit' : True,
    'settable' : True,
}
config['station-add']={
    'valueInit' : False,
    'brokerInit' : False,
    'broker_func' : create_station,
    'settable' : True,
}
config['stations']={
    'valueInit' : {},
    'brokerInit' : True,
    'broker_func' : handle_stations,
    'settable' : True,
}
config['refresh-interval']={
    'valueInit' : 10.,
    'brokerInit' : True,
    'format' : "1:10000",
    'settable' : True,
    'unit': 'min',
}
order = list(config.keys())
order.remove('stations')
order.insert(0, 'stations')
initNodes['config'] = config

stationBikesInitDict = {
    'valueInit' : 0,
    'brokerInit' : False,
}

def get_number_of_bikes(pB):
    pB.dev.stations[pB.dev.stationsName[pB.param.split('/')[0]]].get_number_of_bikes()
    pB.device(False)

stationGetBikesInitDict = {
    'valueInit' : False,
    'brokerInit' : False,
    'broker_func' : get_number_of_bikes,
    'settable' : True,
}

class Station():
    def __init__(self, dev, uid, name):
        self.dev = dev
        self.devisor = dev.devisor
        self.name = name
        self.uid = uid
        self.init_params()

    def init_params(self):
        self.dev.create_property('bikes', self.name, stationBikesInitDict)
        self.dev.create_property('get-info', self.name, stationGetBikesInitDict)
        self.get_number_of_bikes()

    def get_number_of_bikes(self):
        stationDict = self.get_info()
        self.dev.params[self.name+'/bikes'].value = int(
                stationDict['countries'][0]['cities'][0]['places'][0]['bikes'])
        self.dev.params[self.name+'/bikes'].publish_value()

    def get_info(self):
        urlstr = 'place='
        r = requests.get(self.dev.baseurl + urlstr + str(self.uid))
        return r.json()

    def exit(self):
        self.dev.remove_property('bikes', self.name)
        self.dev.remove_property('get-info', self.name)


class DeviceClass(DeviceBase):
    def init_pre(self):
        self.initNodes = initNodes
        self.headers = { 'User-Agent': 'Shah4oPh',}
        self.baseurl = 'https://api.nextbike.net/maps/nextbike-live.json?'
        self.stations = {}
        self.stationsName = {}
        
    def device_thread(self):
        while self.up:
            self.get_all()
            time.sleep(self.params['config/refresh-interval'].value*60)
    
    def get_all(self):
        for i,uid in enumerate(self.stations):
            self.stations[uid].get_number_of_bikes()

    def create_station(self, uid, name):
        if name in self.stations:
            self.devices.log('Station uid "'
                    +uid
                    +'" already in running.', 30)
        else:
            self.stations[uid] = Station(self, uid, name)
            self.stationsName[name] = uid
            if 'config/stations' in self.params:
                self.params['config/stations'].value[uid] = name
                self.params['config/stations'].publish_value()
