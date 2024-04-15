from threading import Thread
import time
import re

from devisor.devisorbase import DeviceBase, devisor_import

serialPackage = devisor_import(None, "serial", "connection")

# MQTT nodes
initNodes = {}

# Control node
def reconnect_handle(pB):
    """
    Function is used to handle reconnect node.

    Parameters:
    pB (dict): parameter base

    Returns:
    No returns
    """

    pB.dev.params['control/reconnect'].publish_value(False)
    pB.dev.connection.reconnect()

def read_interval_handle(pB):
    """
    Function is used to handle "read-interval" node change.

    Parameters:
    pB (dict): parameter base

    Returns:
    No returns
    """

    # Stop current thread
    pB.dev.stopThreads = True
    pB.dev.loopReader.join()
    pB.dev.stopThreads = False

    # Start new thread
    pB.dev.loopReader = Thread(target = pB.dev.read_loop)
    pB.dev.loopReader.start()


control = {}

control['reconnect'] = {
    'valueInit' : False,
    'broker_func' : reconnect_handle,
    'datatype' : 'boolean',
    'brokerInit' : False,
    'settable' : True,
}

control['read-interval'] = {
    'valueInit' : 60.0,
    'settable' : True,
    'broker_func' : read_interval_handle,
    'unit' : 's'
}

initNodes['control'] = control

# Parameters node

parameters = {}

parameters['pdin-gain'] = {
    'valueInit' : 250,
    'datatype' : 'int',
    'broker_func' : lambda pB: pB.dev.execute(1, pB.dev.params["parameters/pdin-gain"].value),
    'brokerInit' : False,
    'settable' : True,
}

parameters['pd-power-gain'] = {
    'valueInit' : 3,
    'datatype' : 'int',
    'broker_func' : lambda pB: pB.dev.execute(2, pB.dev.params["parameters/pd-power-gain"].value),
    'brokerInit' : False,
    'settable' : True,
}

parameters['vco-phase-offset'] = {
    'valueInit' : 2000,
    'datatype' : 'int',
    'broker_func' : lambda pB: pB.dev.execute(3, pB.dev.params["parameters/vco-phase-offset"].value),
    'brokerInit' : False,
    'settable' : True,
}

parameters['pd-power-offset'] = {
    'valueInit' : 0,
    'datatype' : 'int',
    'broker_func' : lambda pB: pB.dev.execute(4, pB.dev.params["parameters/pd-power-offset"].value),
    'brokerInit' : False,
    'settable' : True,
}

parameters['vco-phase-gain'] = {
    'valueInit' : 0,
    'datatype' : 'int',
    'broker_func' : lambda pB: pB.dev.execute(5, pB.dev.params["parameters/vco-phase-gain"].value),
    'brokerInit' : False,
    'settable' : True,
}



initNodes['parameters'] = parameters


class DeviceClass(DeviceBase):
    """
    Class is used to communicate with FNC device using serial communication.
    """

    def init_pre(self, address="/dev/ttyACM1"):
        """
        This function is used to initialize parameters.

        Parameters:
        address (string): USB port 

        Returns:
        No returns
        """

        self.initNodes = initNodes
        self.address = address

        # Commands
        self.commands = {
            1 : {"message":lambda x: f"1,{x}", "check": lambda x: x in range(0,256), "followups":[6]},
            2 : {"message":lambda x: f"2,{x}", "check": lambda x: x in range(0,8), "followups":[6]},
            3 : {"message":lambda x: f"3,{x}", "check": lambda x: x in range(0,4096), "followups":[6]},
            4 : {"message":lambda x: f"4,{x}", "check": lambda x: x in range(0,4096), "followups":[6]},
            5 : {"message":lambda x: f"5,{x}", "check": lambda x: x in range(0,8), "followups":[6]},
            6 : {"message":lambda x="": "6", "check": None, "followups":[]}
        }

        # Responses
        self.responses = {
            6 : {"split":lambda x: re.findall(": (\d+)", x), "data":lambda x: [int(x[0]), int(x[1]), int(x[2]), int(x[3]), int(x[4])], "topics":["parameters/pdin-gain", "parameters/pd-power-gain", "parameters/vco-phase-offset", "parameters/pd-power-offset", "parameters/vco-phase-gain"]},  
        }

    def init_after(self):
        """
        This function is used to connect to the device after initializing nodes.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.connection = serialPackage.ConnectionClass(devisor=self.devisor, address=self.address, baudrate=9600)

        # Start reading thread
        self.stopThreads = False
        self.loopReader = Thread(target = self.read_loop)
        self.loopReader.start()

    def execute(self, id, value=""):
        """
        Function is used to handle writing and reading of the commands.

        Parameters:
        id (int): message id
        args (list): list of additional message arguments

        Returns:
        No returns
        """

        # Check input
        if self.commands[id]["check"] != None and not self.commands[id]["check"](value):
            self.devisor.log.new_log(f"Value out of range.", "WARNING")
            self.execute(6)
            return
        
        # Send message
        self.connection.write(self.commands[id]["message"](value))

        # Check for response
        if id in self.responses.keys():
            self.read(id)

        # Check for followup
        for id_followup in self.commands[id]["followups"]:
            
            # Send followup
            self.connection.write(self.commands[id_followup]["message"]())

            # Check for followup response
            if id_followup in self.responses.keys():
                self.read(id_followup)

    def read(self, id):
        """
        Function is used to read and process message response.

        Parameters:
        id (int): message id for which response is read

        Returns:
        No returns
        """

        try:
            response = self.connection.read().strip("\r\n")
            data = self.responses[id]["data"](self.responses[id]["split"](response))
            for value, topic in zip(data, self.responses[id]["topics"]):
                if topic != "":
                    self.params[topic].publish_value(value)
        except:
            self.devisor.log.new_log(f"Error reading response of {id}.", "WARNING")

    def read_loop(self):
        """
        Function is used to continuously read status from FNC device.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        last_reading = time.time()-float(self.params['control/read-interval'].value)
        while not self.stopThreads and float(self.params['control/read-interval'].value) > 1e-5:

            if time.time()-last_reading > float(self.params['control/read-interval'].value):
                self.execute(6)

                last_reading = time.time()
            
            time.sleep(0.1)

    def exit_pre(self):
        """
        This function is used to close I2C communication.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.stopThreads = True
        self.connection.close()