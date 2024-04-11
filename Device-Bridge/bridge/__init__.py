from threading import Thread
import time

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

    pB.dev.connection.reconnect()
    pB.dev.params['control/reconnect'].publish_value(False)

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
    'brokerInit' : True,
    'settable' : True,
}

control['read-interval'] = {
    'valueInit' : 20.0,
    'settable' : True,
    'broker_func' : read_interval_handle,
    'unit' : 's'
}

initNodes['control'] = control

# Parameters node
parameters = {}

parameters['frequency'] = {
    'valueInit' : 0.0,
    'datatype' : 'float',
    'broker_func' : lambda pB: pB.dev.execute(1, [pB.dev.params["parameters/frequency"].value]),
    'brokerInit' : False,
    'settable' : True,
    'unit' : 'MHz'
}

initNodes['parameters'] = parameters



class DeviceClass(DeviceBase):
    """
    Class is used to communicate with Bridge device using serial connection.
    """

    def init_pre(self, address="/dev/ttyACM0"):
        """
        This function is used to initialize parameters.

        Parameters:
        address (string): USB port address

        Returns:
        No returns
        """

        self.initNodes = initNodes
        self.address = address

        # Commands
        self.commands = {
            1 : {"message":lambda x=[]: f"RF:FILTER:FREQ {x[0]} MHZ", "followups":[2]},
            2 : {"message":lambda x=[]: "STATUS?", "followups":[]},
            3 : {"message":lambda x=[]: "RF:AGC:TARGET?", "followups":[]},
            4 : {"message":lambda x=[]: "N:divider?", "followups":[]},
        }

        # Responses
        self.responses = {
            2 : {"split":lambda x: x.split(","), "data":lambda x: [int(x[0]), int(x[1]), int(x[2]), float(x[3])/1e6, int(x[4]), int(x[5])], "topics":["", "", "", "parameters/frequency", "", ""]},
            3 : {"split":lambda x: x, "data":lambda x: [float(x)], "topics":[""]},
            4 : {"split":lambda x: x, "data":lambda x: [float(x)], "topics":[""]},     
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

    def execute(self, id, args=[]):
        """
        Function is used to handle writing and reading of the commands.

        Parameters:
        id (int): message id
        args (list): list of additional message arguments

        Returns:
        No returns
        """
        
        # Send message
        self.connection.write(self.commands[id]["message"](args))
        print(self.commands[id]["message"](args))

        # Check for response
        if id in self.responses.keys():
            self.read(id)

        # Check for followup
        for id_followup in self.commands[id]["followups"]:
            
            # Send followup
            self.connection.write(self.commands[id_followup]["message"]())
            print(self.commands[id_followup]["message"]())

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
            print(response)
            data = self.responses[id]["data"](self.responses[id]["split"](response))
            for value, topic in zip(data, self.responses[id]["topics"]):
                if topic != "":
                    self.params[topic].publish_value(value)
        except:
            self.devisor.log.new_log(f"Error reading response of {id}.", "WARNING")

    def read_loop(self):
        """
        Function is used to read status continuously from Bridge device.

        Parameters:
        No parameters

        Returns:
        No returns
        """
        
        last_reading = time.time()-float(self.params['control/read-interval'].value)
        while not self.stopThreads and float(self.params['control/read-interval'].value) > 1e-5:

            if time.time()-last_reading > float(self.params['control/read-interval'].value):
                self.execute(2)
                #self.execute(3)
                #self.execute(4)

                last_reading = time.time()
            
            time.sleep(0.1)

    def exit_pre(self):
        """
        This function is used to close serial communication.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.stopThreads = True
        self.connection.close()