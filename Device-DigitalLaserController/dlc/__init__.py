import time
from threading import Thread
import toptica.lasersdk.dlcpro.v2_6_0 as dlcpro
from toptica.lasersdk.dlcpro.v2_6_0 import DLCpro, NetworkConnection, DeviceNotFoundError, DecopError, UserLevel

from devisor.devisorbase import DeviceBase
from devisor.devices.dlc.structure import *


class DeviceClass(DeviceBase):
    """
    Class is used to communicate with Toptica DLC.
    """

    def init_pre(self, address="localhost", userlevel=3, password=""):
        """
        This function is used to initialize parameters.

        Parameters:
        address (string): ip address 

        Returns:
        No returns
        """

        self.address = address
        self.userlevels = {
            0: {"ul": UserLevel.INTERNAL, "password": "", "name": "INTERNAL"},
            1: {"ul": UserLevel.SERVICE, "password": "", "name": "SERVICE"},
            2: {"ul": UserLevel.MAINTENANCE, "password": "CAUTION", "name": "MAINTENANCE"},
            3: {"ul": UserLevel.NORMAL, "password": "", "name": "NORMAL"},
            4: {"ul": UserLevel.READONLY, "password": "", "name": "READONLY"}
        }

        if userlevel in self.userlevels.keys():
            self.userlevel = self.userlevels[userlevel]
            if userlevel in [0, 1]:
                self.userlevel["password"] = password
        else:
            self.userlevel = self.userlevels[3]
            self.devisor.log.new_log(f"User level out of range. Set to \"NORMAL\".", "WARNING")

        self.initNodes, self.components = build_mqtt_nodes(self)

        self.no_subscription = {
            "laser1.recorder.data.zoom_data",
            "laser1.scope.data",
            "laser2.recorder.data.zoom_data",
            "laser2.scope.data",
        }


    def init_after(self):
        """
        This function is used to initialize after initializing nodes.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.connect()
        self.subscribe()

        # Start reading thread
        self.stopThreads = False
        self.loopReader = Thread(target = self.read_loop)
        self.loopReader.start()

    def connect(self):
        """
        This function is used to connect to the DLC.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.connection = DLCpro(NetworkConnection(self.address))
        self.connection.open()

        try: 
            self.connection.change_ul(self.userlevel["ul"], self.userlevel["password"])
            self.devisor.log.new_log(f"Connected as {self.userlevel['name']}.", "INFO")
        except Exception as e:
            self.connection.change_ul(UserLevel.NORMAL, "")
            self.devisor.log.new_log(f"Incorrect password. Connected as \"NORMAL\".", "WARNING")

    def disconnect(self):
        """
        This function is used to disconnect from the DLC.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.connection.close()

    def subscribe(self):
        """
        This function is used to subscribe to DLC parameters.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.subscriptions = {}

        for component in self.components:
            if component in self.no_subscription:
                continue

            try:
                current = self.connection
                for i in component.split("."):
                    current = getattr(current, i)
                subscribe_function = getattr(current, "subscribe")
                self.subscriptions[component] = subscribe_function(self.subscribe_callback)
            except Exception as e:
                self.devisor.log.new_log(f"Failed to subscribe to \"{component}\".", "WARNING")

    def subscribe_callback(self, subscription, timestamp, value):
        """
        This function is used as a callback function for subscriptions.

        Parameters:
        subscription (object): subscription object
        timestamp (string): timestamp
        value (object): value object

        Returns:
        No returns
        """
        
        try:
            if len(subscription.name.split(":")) == 1:
                self.params[f"system/{subscription.name.replace(':', '/')}"].publish_value(value.get())
            else:
                self.params[subscription.name.replace(':', '/')].publish_value(value.get())
        except Exception as e:
            pass

    def read_loop(self):
        """
        This function is used exiting.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        last_reading = time.time()-float(self.params['control/read-interval'].value)
        while not self.stopThreads and float(self.params['control/read-interval'].value) > 1e-5:

            if time.time()-last_reading > float(self.params['control/read-interval'].value):
                self.connection.poll()

                last_reading = time.time()
            
            time.sleep(0.1)

    def exit_pre(self):
        """
        This function is used exiting.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.stopThreads = True
        self.disconnect()