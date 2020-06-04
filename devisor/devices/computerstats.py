#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io
# Viktor Messerer: viktor.messerer@uibk.ac.at

import psutil
import os
from time import sleep as wait

from devisor.devisorbase import DeviceBase


initNodes = {}

control = {}
control['refresh-interval']={
    'valueInit' : 5.,
    'brokerInit' : True,
    'format' : "0.1:100",
    'settable' : True,
    'unit': 's',
}

initNodes['control'] = control

laptop={}
for i in range(psutil.cpu_count()):
    laptop['cpu'+ str(i) +'/cpu_percent'] ={
        'valueInit' : 0.,
        'brokerInit' : False,
        'unit': '%',
    }
    laptop['cpu'+ str(i) +'/cpu_freq'] ={
        'valueInit' : 0.,
        'brokerInit' : False,
        'unit': 'MHz',
    }

laptop['illuminance']= {
    'valueInit' : 0.,
    'brokerInit' : False,
}

laptop['battery']= {
    'valueInit' : 0.,
    'brokerInit' : False,
    'unit': '%',
}

initNodes['laptop']=laptop

class computerstats(DeviceBase):
    def init_pre(self):
        self.initNodes = initNodes
        
    def device_thread(self):
        while self.up:
            self.get_all_properties()
            wait(self.params['control/refresh-interval'].value)
    
    def get_all_properties(self):
        self.get_illuminance()
        self.get_cpu_usage()
        self.get_battery()
                
    def property_update_thread(self):
        while True:
            self.get_all_properties()
            wait(self.params['control/refresh-interval'].value)
            
    def get_cpu_usage(self):
        cpuusage = psutil.cpu_percent(percpu=True)
        cpufreq = psutil.cpu_freq(percpu=True)
        for i in range(psutil.cpu_count()):
            self.params['laptop/cpu'+ str(i) +'/cpu_percent'].device(cpuusage[i])
            self.params['laptop/cpu'+ str(i) +'/cpu_freq'].device(cpufreq[i].current)
            
    def get_battery(self):
        try: 
            self.params['laptop/battery'].device(psutil.sensors_battery().percent)
        except:
            self.params['laptop/battery'].device(0)
    
    def get_illuminance(self):
        try:
            directory = self.find_all('in_illuminance_raw','/sys/devices/')[0]
            f=open(directory,'r')
            content=int(f.read())
            #print(content)
            #self.properties['channel']['illuminance'] = content
            f.close()
        except:
            content = 0
        self.params['laptop/illuminance'].device(content)
            
    def find_all(self, name, path):
        result = []
        for root, dirs, files in os.walk(path):
            if name in files:
                result.append(os.path.join(root, name))
        return result
