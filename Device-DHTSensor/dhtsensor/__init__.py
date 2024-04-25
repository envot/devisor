from threading import Thread
import time
import board
import adafruit_dht

from devisor.devisorbase import DeviceBase, devisor_import

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

    try:
        pB.dev.dhtSensor.exit()
    except:
        pass
    try:
        pB.dev.dhtSensor = adafruit_dht.DHT11(board.D4, use_pulseio=False)
    except:
        pB.dev.dhtSensor = None
        pB.dev.devisor.log.new_log(f"Reconnection unsucessful.", "WARNING")

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

parameters['temperature'] = {
    'valueInit' : 0,
    'datatype' : 'int',
    'brokerInit' : True,
    'settable' : True,
    'unit' : '°C'
}

parameters['humidity'] = {
    'valueInit' : 0,
    'datatype' : 'int',
    'brokerInit' : True,
    'settable' : True,
    'unit' : '%'
}

initNodes['parameters'] = parameters


class DeviceClass(DeviceBase):
    """
    Class is used to communicate with DHT11 sensor.
    """

    def init_pre(self):
        """
        This function is used to initialize parameters.

        Parameters:
        No parameters 

        Returns:
        No returns
        """

        self.initNodes = initNodes

    def init_after(self):
        """
        This function is used to connect to the device after initializing nodes.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        try:
            self.dhtSensor = adafruit_dht.DHT11(board.D4, use_pulseio=False)
        except Exception as error:
            self.dhtSensor = None
            self.devisor.log.new_log(f"Connection failed with error: {error}", "WARNING")

        # Start reading thread
        self.stopThreads = False
        self.loopReader = Thread(target = self.read_loop)
        self.loopReader.start()

    def read(self):

        try:
            self.params["parameters/temperature"].publish_value(self.dhtSensor.temperature)
            self.params["parameters/humidity"].publish_value(self.dhtSensor.humidity)
        except RuntimeError as error:
            # Errors happen fairly often, DHT's are hard to read, just keep going
            pass
        except Exception as error:
            self.devisor.log.new_log(f"Reading failed with error: {error}", "WARNING")
    
    def read_loop(self):
        """
        Function is used to continuously read temperature and humidity from DHT11 sensor.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        last_reading = time.time()-float(self.params['control/read-interval'].value)
        while not self.stopThreads and float(self.params['control/read-interval'].value) > 1e-5:

            if self.dhtSensor != None and time.time()-last_reading > float(self.params['control/read-interval'].value):
                self.read()

                last_reading = time.time()
            
            time.sleep(0.1)

    def exit_pre(self):
        """
        This function is used to exit class.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.stopThreads = True
        self.dhtSensor.exit()