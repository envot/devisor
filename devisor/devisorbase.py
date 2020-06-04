#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io


import time
import traceback

import paho.mqtt.client as mqttClient

import _thread

from .mqttlog import MQTTLog
from .paramProcess import init_param_property
from .params import initDeviceAttributes,initNodeAttributes

HOMIE_SET = "/set"

def keep_private_parameter(pB):
    if pB.value != pB.valueOld:
        pB.value = pB.valueOld
        pB.publish_value()
        pB.dev.log.new_log("Somebody tried to change "
                +str(pB.param))


class DeviceBase():
    def __init__(self, devisor, topicFolder, address=False):
        self.devisor = devisor
        self.dev = self
        self.address = address
        self.ip = self.devisor.ip
        self.topicFolder = topicFolder
        self.name = topicFolder
        self.subscribed = []

        self.init_basics()
        self.init_pre()
        self.init_standards()
        self.init_after()

    def init_basics(self):
        self.log = MQTTLog(self)
        self._connect_mqtt_client()
        self._get_persistent()
        if '$state' in self.initBrokerMsgs:
            if self.initBrokerMsgs['$state'] in ['ready', 'init']:
                self.client.unsubscribe(self.topicFolder+'/#')
                self.client.loop_stop()
                self.client.disconnect()
                raise Exception('Device "'+self.topicFolder
                        +'" is already running.')
        if ('$implementation' in self.initBrokerMsgs
                and self.address == 'persistent'):
            self.address = self.initBrokerMsgs['$implementation']
        self.params = {}
        self._init_device_attributes()
        self.log.init_mqtt()

    def init_pre(self):
        pass

    def init_standards(self):
        self._init_nodes()
        self.init_device_params()
        self.start_threads()
        self.publish_all()

    def init_after(self):
        pass

    def start_threads(self):
        self.up = True
        self.deviceThread = _thread.start_new_thread ( self.device_thread, () )
        self.uptimeThread = _thread.start_new_thread ( self._uptime_thread, () )
        self.params['$state'].device('ready')

    def device_thread(self):
        pass

    def init_device_params(self):
        pass
        
    def exit_pre(self):
        pass

    def exit(self):
        self.exit_pre()
        self.up = False
        self.params['$state'].device('disconnected')
        self.log.new_log("Devcie closed.")
        self.client.loop_stop()
        self.client.disconnect()


    def remove_topic(self, topic):
        self.client.publish(self.topicFolder+'/'+topic, None, qos=1,
                retain=True)

    def subscribe_topic(self, topic):
        self.client.subscribe(self.topicFolder+'/'+topic)

    def unsubscribe_topic(self, topic):
        self.client.unsubscribe(self.topicFolder+'/'+topic)

    def publish_topic(self, topic, payload):
        self.client.publish(self.topicFolder+'/'+topic, payload, qos=1,
                retain=True)

    def publish_all(self, attributes=True):
        for param in self.params:
            if attributes or (not attributes and not '$' in param):
                self.params[param].publish_value()


    def broker_init(self, topicName, topicMessage):
        self.initBrokerMsgs[topicName] = topicMessage

    def broker_run(self, topicNameSet, topicMessage):
        topicName = topicNameSet[:-len(HOMIE_SET)]
        if topicNameSet[-len(HOMIE_SET):] == HOMIE_SET and topicMessage!="":
            self.remove_topic(topicNameSet)
            try:
                self.publish_topic(topicName, topicMessage)
                self.params[topicName].broker(topicMessage)
            except:
                self.log.new_log(traceback.format_exc(), 'CRITICAL')
                self.params[topicName].value = self.params[topicName].valueOld
                self.params[topicName].publish_value()


    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            if self.up:
                self.log.new_log("Reconnected to broker: "+str(self.devisor.host)+":"
                    +str(self.devisor.port))
                self.params['$state'].device('ready')
                for topic in self.subscribed:
                    self.subscribe_topic(topic)
                self.publish_all()
                self.log.new_log("Resubscribed and refreshed all topics.")
            else:
                self.log.new_log("Connected to broker: "+str(self.devisor.host)+":"
                    +str(self.devisor.port))
        else:
            print(self.log.logMessage)
            print("Connection failed")

    def on_message(self, client, userdata, message):
        topicFolder = self._topic_folder(message.topic)
        topicName = message.topic[len(topicFolder)+1:]
        topicMessage = message.payload.decode()
        if topicFolder == self.topicFolder:
            self.broker(topicName, topicMessage)
        else:
            self.otherMessage(topicFolder, topicName, topicMessage)

    def otherMessage(self, topicFolder, topicName, payload):
        self.log.new_log('Device "'+topicFolder+'" not found.', 'DEBUG')
        pass

    def create_node(self, node):
        if not node in self.params['$nodes'].value:
            self.params['$nodes'].value.append(node)
            for attr in initNodeAttributes:
                self._init_param(node+'/'+attr, initNodeAttributes[attr])

    def remove_node(self, node):
        if node in self.params['$nodes'].value:
            self.params['$nodes'].value.remove(node)
            self.params['$nodes'].publish_value()
        for param in self.params:
            if param[:len(node)] == node:
                self.params[param].close()

    def create_property(self, name, node, initDict): 
        self.create_node(node)
        param = node+'/$properties'
        if not name in self.params[param].value:
            self.params[param].value.append(name)
        self._init_param(node+'/'+name, initDict)

    def remove_property(self, name, node): 
        paramProp = node+'/$properties'
        if name in self.params[paramProp].value:
            self.params[paramProp].value.remove(name)
            self.params[paramProp].publish_value()
        self.unsubscribe_topic(paramProp+HOMIE_SET)
        for param in self.params:
            if param[:len(node+'/'+name)] == node+'/'+name:
                self.params[param].close()
        if len(self.params[paramProp].value) == 0:
            self.remove_node(node)


    def _connect_mqtt_client(self):
        self.client = mqttClient.Client(self.topicFolder)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.will_set(self.topicFolder+"/$state",
                'lost', qos=0, retain=True)
        self.client.connect(self.devisor.host, self.devisor.port)
        self.log.new_log("Connected: "
                +self.devisor.host
                +":"+str(self.devisor.port))
        self.client.loop_start()

    def _get_persistent(self):
        self.initBrokerMsgs = {}
        self.broker = self.broker_init
        self.client.subscribe(self.topicFolder+'/#')
        self.log.new_log("Subscribed : "
                +self.topicFolder+"/#",
                'DEBUG')
        time.sleep(1)
        self.client.unsubscribe(self.topicFolder+'/#')
        self.log.new_log("Unsubscribed : "+self.topicFolder+"/#",
                'DEBUG')
        self.broker = self.broker_run

    def _init_device_attributes(self):
        for attribute in initDeviceAttributes:
            self._init_param(attribute, initDeviceAttributes[attribute])


    def _init_nodes(self):
        for node in self._order_dict(self.initNodes):
            self.create_node(node)
            self._init_node_content(node)
        self.initNodes = {}

    def _init_node_content(self, node):
        for prop in self._order_dict(self.initNodes[node]):
            self.create_property(prop, node, self.initNodes[node][prop])

    def _init_param_attribute(self, param, value):
        initAttrDict = {}
        initAttrDict['broker_func'] = keep_private_parameter
        initAttrDict['valueInit'] = value
        init_param_property(self, param, initAttrDict)
    

    def _init_param_attributes(self, param, initDict):
        self._init_param_attribute(param+'/$name', param)
        if 'datatype' in initDict:
            self._init_param_attribute(param+'/$datatype', initDict['datatype'])
        else:
            self._init_param_attribute(param+'/$datatype',
                    self._datatype(type(initDict['valueInit'])))
        if 'settable' in initDict:
            if initDict['settable']:
                self._init_param_attribute(param+'/$settable', 'true')
        if 'format' in initDict:
            self._init_param_attribute(param+'/$format', initDict['format'])
        if 'unit' in initDict:
            self._init_param_attribute(param+'/$unit', initDict['unit'])

    def _init_param(self, param, initDict):
        name = param.split('/')[-1]
        if not (name[0] == '$' or param[0] == '$'):
            self._init_param_attributes(param, initDict.copy())
            self.subscribe_topic(param+HOMIE_SET)
            self.subscribed.append(param+HOMIE_SET)
        return init_param_property(self, param, initDict.copy())


    def _order_dict(self, initDict):
        if 'order' in initDict:
            order = initDict['order']
            del(initDict['order'])
        else:
            order = list(initDict.keys())
        return order

    def _topic_folder(self, topic, length=2):
        topicArray = topic.split('/')
        topicFolder = '/'.join(topicArray[:length])
        return topicFolder

    def _datatype(self, datatype):
        if datatype == bool:
            return 'boolean'
        if datatype == int:
            return 'integer'
        if datatype == float:
            return 'float'
        if datatype in [str, dict]:
            return 'string'
        if datatype == list:
            return 'string'
    

    def _uptime_thread(self):
        self.startTime = time.time()
        time.sleep(5)
        while self.up:
            self.params['$name'].publish_value()
            self.params['$stats/uptime'].value = time.time()-self.startTime
            self.params['$stats/uptime'].publish_value()
            time.sleep(self.params['$stats/interval'].value*0.9)

