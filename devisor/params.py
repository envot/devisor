#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

initLogging = {}

def new_log(pB):
    if pB.value != pB.valueOld:
        pB.value = pB.valueOld
        pB.publish_value()

def length_change(pB):
    pB.dev.log.length = pB.value
    pB.dev.log.new_log('Changed log length to '+str(pB.value))

def level_change(pB):
    pB.dev.log.change_level(pB.value)


logging = {
    'length' : {
        'broker_func' : length_change,
        'valueInit' : 20,
        'settable' : True,
        'brokerInit' : True,
        'format' : "0:1000",
    },
    'logs' : {
        'valueInit' : 'New Log',
        'broker_func' : new_log,
        'brokerInit' : True,
    },
    'level' : {
        'broker_func' : level_change,
        'valueInit' : 'DEBUG',
        'datatype' : 'enum',
        'settable' : True,
        'brokerInit' : True,
        'format' : "DEBUG,INFO,WARNING,ERROR,CRITICAL",
        },
}
order = list(logging.keys())
order.remove('logs')
order.insert(0, 'logs')
logging['order'] = order
initLogging['zlogging'] = logging



def get_name(pB):
    pB.value = pB.param.split('/')[0]
    pB.publish_value()

initNodeAttributes = {
    '$name' : {
        'valueInit' : 'NodeNewName',
        'device_func' : get_name,
        },
    '$type' : {
        'valueInit' : 'NoteType',
        },
    '$properties' : {
        'valueInit' : [], 
        },
}



def get_name(pB):
    pB.value = pB.dev.topicFolder
    pB.publish_value()

def get_ip(pB):
    pB.value = pB.dev.ip
    pB.publish_value()

def get_impl(pB):
    pB.value = pB.dev.address
    pB.publish_value()

initDeviceAttributes = {
    '$homie' : {
        'valueInit' : '4.0.0',
    },
    '$name' : {
        'valueInit' : 'some Name',
        'device_func' : get_name,
    },
    '$state' : {
        'valueInit' : 'init',
    },
    '$localip' : {
        'valueInit' : 'localhost',
        'device_func' : get_ip,
    },
    '$mac' : {
        'valueInit' : 'not known',
    },
    '$fw/version' : {
        'valueInit' : 'not known',
    },
    '$fw/name' : {
        'valueInit' : 'not known',
    },
    '$implementation' : {
        'valueInit' : 'impl',
        'device_func' : get_impl,
    },
    '$stats' : {
        'valueInit' : 'uptime',
    },
    '$stats/uptime' : {
        'valueInit' : 0.,
    },
    '$stats/interval' : {
        'valueInit' : 60,
    },
    '$nodes' : {
        'valueInit' : [],
    },
}
