#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io

import time
import select
import re
import queue
from threading import Thread

from devisor.devisorbase import DeviceBase, devisor_import
from devisor.devices.rgamks113.structure import *
from devisor.devices.rgamks113.sync_messages import *
from devisor.devices.rgamks113.async_messages import *

tcpPackage = devisor_import(None, 'tcpsocket', 'connection')



# Class for communication with the RGAMKS113 device
class DeviceClass(DeviceBase):
    """
    Class is used to communicate with RGAMKS113 device over tcp connection.
    """

    def init_pre(self, address = '10.187.144.117:10014'):
        """
        This function is used to initialize parameters.

        Parameters:
        address (string): network address of the RGAMKS113

        Returns:
        No returns
        """

        self.address = address
        self.initNodes = initNodes
        self.asyncNotification = asyncNotification
        self.syncResponse = syncResponse
        self.maxFilamentOnTime = 3600 # in seconds
        self.maxMass = 100 # in amu
        self.maxOnTime = 43200 # in seconds
        self.currentMeasurement = ''
        self.measurementsRemaining = 0
        self.totalPressure = 0 # in mbar
        self.addedMeasurements = dict()
        self.readNow = False
        self.readPressureTimeout = 10
        self.initialized = False
        self.messageQueueSync = queue.Queue()
        self.messageQueueAsync = queue.Queue()

    def connect(self):
        """
        This function is used to connect to the RGAMKS113 and start all threads.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        try:
            self.connection = tcpPackage.ConnectionClass(devisor=self.devisor, address=self.address)
        except:
            self.params['connection/connect'].publish_value(False)
            self.dev.log.new_log("Unable to connect to the device.", "ERROR")
            return

        self.asyncThreadsStop = False
        self.asyncListener = Thread(target = self.listener)
        self.asyncHandler = Thread(target = self.async_communication)
        self.asyncListener.start()
        self.asyncHandler.start()

    def disconnect(self):
        """
        This function is used to disconnect from the RGAMKS113 and stop all threads.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.client.unsubscribe('agilentxgs600/+/pressure/img1')
        self.sync_communication("ScanStop\n")
        self.sync_communication(f"MeasurementRemoveAll\n")
        self.sync_communication('FilamentControl Off\n')
        while self.dev.params['filament/state'].value != "OFF":
            continue
        self.sync_communication('Release\n')
        self.asyncThreadsStop = True
        self.asyncListener.join()
        self.asyncHandler.join()

        try:
            self.connection.close()
        except:
            self.params['connection/connect'].publish_value(True)
            self.dev.log.new_log("Unable to disconnect from the device.", "ERROR")


    def init_communication(self):
        """
        This function is used to gain control of the sensor and read some initial data from it.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.sync_communication('AcceptProtocol 1.8\n')
        self.sync_communication('Control "RGA_Controller" "1.0"\n')
        self.sync_communication('Info\n')
        self.sync_communication(f'FilamentOnTime {self.maxFilamentOnTime}\n')
        self.sync_communication('FilamentInfo\n')
        self.dev.params['filament/time-on'].publish_value(self.maxFilamentOnTime)

        # Subscribe to Agilent XGS-600
        self.client.subscribe(f"{self.dev.params['filament/pressure-sensor'].value}")

    def otherMessage(self, topicFolder, topicName, payload):
        """
        This function listens for pressure change on Agilent XGS-600 and stores the last value.

        Parameters:
        topicFolder (string): topic folder
        topicName (string): topic name
        payload (string): value

        Returns:
        No returns
        """

        self.totalPressure = float(payload)
        self.readNow = False
        

    def sync_communication(self, message):
        """
        This function is used to handle sync messages.

        Parameters:
        message (string): message that is to be sent to the RGAMKS113

        Returns:
        No returns
        """

        self.connection.write(message)
        name, response = self.messageQueueSync.get()

        # Handle response message
        is_ok = self.syncResponse[name](self, response)

        return is_ok
    
    def async_communication(self):
        """
        This function is used to handle async messages.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        while not self.asyncThreadsStop:
            if self.messageQueueAsync.empty():
                continue

            name, notification = self.messageQueueAsync.get()

            # Handle notification
            if self.asyncNotification[name] != None:
                self.asyncNotification[name](self, notification)

    def listener(self):
        """
        This function is used to listen and sort (sync / async) messages from the RGAMKS113. 
        Messages are sorted into two spearate queues depending on whether the message is sync or async one. 

        Parameters:
        No parameters

        Returns:
        No returns
        """

        messageStream = ''
        while not self.asyncThreadsStop:
            r, _, _ = select.select([self.connection.instr], [], [], 0)
            if len(r) > 0:
                messageStream += self.connection.read()
            
            temp = messageStream.split('\r\r', 1)

            if len(temp) >= 2:
                message, messageStream = temp[0], temp[1]
                name = re.match('(?P<name>[^\s]+)?.*', message)['name']

                # Store async message
                if name in self.asyncNotification.keys():
                    self.messageQueueAsync.put((name, message))

                # Store sync message
                else:
                    self.messageQueueSync.put((name, message))

    def num_of_measurements(self):
        """
        This function calculates number of measurements to perform in num-of-scans number of scans.

        Parameters:
        No parameters

        Returns:
        (int): Number of datapoints to collect
        """

        temp = 0
        for i in self.params['scan/list'].value.split(","):
            temp += self.addedMeasurements[i]["num-of-measurements"]

        return temp*int(self.dev.params['scan/num-of-scans'].value)

    def repeat_scan(self):
        """
        This function is used to run scan repeatedly with certain interval time.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.measurementsRemaining = self.num_of_measurements()
        temp = self.measurementsRemaining
        lastScanTime = time.time()
        self.sync_communication(f"ScanStart {self.dev.params['scan/num-of-scans'].value}\n")


        # Repeat scans
        while (self.dev.params['scan/repeat'].value or self.measurementsRemaining > 0) and \
              not self.asyncThreadsStop:
            
            if not self.dev.params['filament/control'].value:
                self.dev.params['filament/control'].value = True
                self.dev.publish_topic('filament/control/set', "true")

            if self.dev.params['filament/state'].value == "ON" and \
               time.time()-lastScanTime > self.dev.params['scan/interval'].value and \
               self.measurementsRemaining == 0 and \
               self.dev.params['scan/repeat'].value:
                self.measurementsRemaining = temp
                lastScanTime = time.time()
                self.sync_communication(f"ScanResume {self.dev.params['scan/num-of-scans'].value}\n")

        # Stop scan if not already stopped
        if self.params['scan/start-stop'].value:
            self.sync_communication("ScanStop\n")
            self.params['scan/start-stop'].publish_value(False)
            self.params['scan/list'].publish_value('')
            self.params['scan/current-scan'].publish_value('')
            self.params['scan/current-measurement'].publish_value('')
            



    def exit_pre(self):
        """
        This function is used to join all threads, release the control of the RGAMKS113 and 
        close the tcp connection.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.disconnect()