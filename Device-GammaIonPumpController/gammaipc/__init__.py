from threading import Thread
import time
import re

from devisor.devisorbase import DeviceBase, devisor_import

telnetPackage = devisor_import(None, 'telnet', 'connection')

# Nodes
initNodes = {}

# High voltage control
def read_interval_handle(pB):
    """
    Function is used to handle "read-interval" node change.

    Parameters:
    pB : parameter base

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

def start_stop_handle(pB):
    """
    Function is used to start/stop pump.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/start-stop'].value:
        pB.dev.set("start pump")

    else:
        pB.dev.set("stop pump")

    pB.dev.get("supply status")

def status_handle(pB):
    """
    Function is used to get pump status.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    pB.dev.get("supply status")


control = {}

control['read-interval'] = {
    'valueInit' : 60.0,
    'settable' : True,
    'broker_func' : read_interval_handle,
    'unit' : 's'
}

control['supply-status'] = {
    'valueInit' : "",
    'settable' : True,
    'broker_func' : status_handle,
}

control['start-stop'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : start_stop_handle,
}

initNodes['control'] = control


# Parameters node
def pump_size_handle(pB):
    """
    Function is used to set pump size.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    pB.dev.set("pump size", [pB.dev.params['parameters/pump-size'].value])

def initiate_hipot_handle(pB):
    """
    Function is used to initiate high potential operation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['parameters/high-potential/initiate'].value:
        pB.dev.set("initiate hipot")

    pB.dev.params['parameters/high-potential/initiate'].publish_value(False)

def target_voltage_handle(pB):
    """
    Function is used to set target voltage.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    pB.dev.set("target voltage", [pB.dev.params['parameters/target-voltage'].value])

def setpoint_handle(pB):
    """
    Function is used to parameters setpoint.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['parameters/setpoint/configure'].value:
        pB.dev.set("setpoint", [1, pB.dev.params['parameters/setpoint/configure/mode'].value, pB.dev.params['parameters/setpoint/configure/on-pressure'].value, pB.dev.params['parameters/setpoint/configure/off-pressure'].value])

    pB.dev.params['parameters/setpoint/configure'].publish_value(False)

def calibration_factor_handle(pB):
    """
    Function is used to set calibration factor.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    pB.dev.set("calibration factor", [pB.dev.params['parameters/calibration-factor'].value])

def foldback_enable_handle(pB):
    """
    Function is used to enable/disable foldback.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    pB.dev.set("foldback enable", [pB.dev.params['parameters/foldback/enable'].value])


def foldback_voltage_handle(pB):
    """
    Function is used to set foldback voltage.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    pB.dev.set("foldback voltage", [pB.dev.params['parameters/foldback/voltage'].value])

def foldback_pressure_handle(pB):
    """
    Function is used to set foldback pressure.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    pB.dev.set("foldback pressure", [pB.dev.params['parameters/foldback/pressure'].value])

def auto_restart_handle(pB):
    """
    Function is used to set auto restart mode.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    try:
        pB.dev.set("auto restart", [pB.dev.params['parameters/auto-restart'].value])
    except:
        pB.dev.log.new_log("Invalid auto restart mode.", "WARNING")
        pB.dev.get("auto restart")

def hv_enable_handle(pB):
    """
    Function is used to cofigure high voltage settings.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    try:
        pB.dev.set("hv autorecovery", [pB.dev.params['parameters/high-voltage/mode'].value])
    except:
        pB.dev.log.new_log("Invalid high voltage setting.", "WARNING")
        pB.dev.get("hv autorecovery")

def hv_jumpstart_handle(pB):
    """
    Function is used to enable/disable jumpstart.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    pB.dev.set("hv jumpstart", [pB.dev.params['parameters/high-voltage/jumpstart'].value])


parameters = {}

parameters['current'] = {
    'valueInit' : 0.0,
    'settable' : True,
    'unit' : 'A'
}

parameters['voltage'] = {
    'valueInit' : 0.0,
    'settable' : True,
    'unit' : 'V'
}

parameters['pressure'] = {
    'valueInit' : 0.0,
    'settable' : True,
    'unit' : 'mbar'
}

parameters['pump-size'] = {
    'valueInit' : 0,
    'settable' : True,
    'broker_func' : pump_size_handle,
    'unit' : 'L/s'
}

parameters['setpoint/mode'] = {
    'valueInit' : "OFF",
    'settable' : True,
    'format' : ["OFF", "PRESSURE", "ERROR"]
}

parameters['setpoint/on-pressure'] = {
    'valueInit' : 0.0,
    'settable' : True,
}

parameters['setpoint/off-pressure'] = {
    'valueInit' : 0.0,
    'settable' : True,
    'unit' : 'mbar'
}

parameters['setpoint/configure'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : setpoint_handle,
}

parameters['setpoint/configure/mode'] = {
    'valueInit' : "OFF",
    'settable' : True,
    'format' : ["OFF", "PRESSURE", "ERROR"]
}

parameters['setpoint/configure/on-pressure'] = {
    'valueInit' : 0.0,
    'settable' : True,
    'unit' : 'mbar'
}

parameters['setpoint/configure/off-pressure'] = {
    'valueInit' : 0.0,
    'settable' : True,
    'unit' : 'mbar'
}

# # Command not working
# parameters['calibration-factor'] = {
#     'valueInit' : 0.0,
#     'settable' : True,
#     'broker_func' : calibration_factor_handle,
# }

parameters['high-potential/initiate'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : initiate_hipot_handle,
}

parameters['high-potential/target-voltage'] = {
    'valueInit' : 0.0,
    'settable' : True,
    'broker_func' : target_voltage_handle,
    'unit' : 'V'
}

parameters['foldback/enable'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : foldback_enable_handle,
}

parameters['foldback/voltage'] = {
    'valueInit' : 0.0,
    'settable' : True,
    'broker_func' : foldback_voltage_handle,
    'unit' : 'V'
}

parameters['foldback/pressure'] = {
    'valueInit' : 0.0,
    'settable' : True,
    'broker_func' : foldback_pressure_handle,
    'unit' : 'mbar'
}

parameters['auto-restart'] = {
    'valueInit' : "DISABLE",
    'settable' : True,
    'format' : ["DISABLE", "POWER AND HV", "ONLY POWER"],
    'broker_func' : auto_restart_handle,
}

parameters['high-voltage/mode'] = {
    'valueInit' : "DISABLE",
    'settable' : True,
    'format' : ["DISABLE", "INTERLOCK", "ON/OFF"],
    'broker_func' : hv_enable_handle,
}

parameters['high-voltage/jumpstart'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : hv_jumpstart_handle,
}



initNodes['parameters'] = parameters



class DeviceClass(DeviceBase):
    """
    This class is used to communicate with Gamma Ion Vacuum Pump Controller device over the Telnet connection.
    """

    def init_pre(self, address="10.187.144.25:23"):
        """
        Constructor of the class.

        Parameters:
        port_name (string): IP address and port

        Returns:
        No returns
        """

        self.initNodes = initNodes
        self.address = address

        self.auto_restart = {
            "DISABLE":"NO", "NO":"DISABLE",
            "POWER AND HV":"YES", "YES":"POWER AND HV",
            "ONLY POWER":"POWER", "POWER":"ONLY POWER",
        }

        self.hv_enable = {
            "ON/OFF":"YES", "YES":"ON/OFF",
            "DISABLE":"NO", "NO":"DISABLE",
            "INTERLOCK":"INTERLOCK"
        }

        self.setpoint_mode = {
            "OFF":"1", "1":"OFF",
            "PRESSURE":"0", "0":"PRESSURE",
            "ERROR":"-1", "-1":"ERROR"
        }

        # Get commands
        self.get_commands = {
            "supply status": {"command":"spc 0D", "topics":("control/supply-status",), "transform":lambda s,x:x},
            "current": {"command":"spc 0A", "topics":("parameters/current",), "transform":lambda s,x:[float(i) for i in x]},
            "pressure": {"command":"spc 0B", "topics":("parameters/pressure",), "transform":lambda s,x:[float(i) for i in x]},
            "voltage": {"command":"spc 0C", "topics":("parameters/voltage",), "transform":lambda s,x:[float(i) for i in x]},
            "pump size": {"command":"spc 11", "topics":("parameters/pump-size",), "transform":lambda s,x:[int(i) for i in x]},
            "calibration factor": {"command":"spc 1D", "topics":("parameters/calibration-factor",), "transform":lambda s,x:[float(i) for i in x]},
            "setpoint": {"command":"spc 3C", "topics":("", "parameters/setpoint/mode", "parameters/setpoint/on-pressure", "parameters/setpoint/off-pressure", ""), "transform":lambda s,x:[x[0], s.setpoint_mode[x[1].upper()], float(x[2]), float(x[3]), x[4]]},
            "target voltage": {"command":"spc 53", "topics":("parameters/high-potential/target-voltage",), "transform":lambda s,x:[float(i) for i in x]},
            "foldback enable": {"command":"spc 56", "topics":("parameters/foldback/enable",), "transform":lambda s,x:[True if i == "YES" else False for i in x]},
            "foldback voltage": {"command":"spc 54", "topics":("parameters/foldback/voltage",), "transform":lambda s,x:[float(i) for i in x]},
            "foldback pressure": {"command":"spc 55", "topics":("parameters/foldback/pressure",), "transform":lambda s,x:[float(i) for i in x]},
            "is pump on": {"command":"spc 61", "topics":("control/start-stop",), "transform":lambda s,x:[True if i == "YES" else False for i in x]},
            "auto restart": {"command":"spc 34", "topics":("parameters/auto-restart",), "transform":lambda s,x:[s.auto_restart[i.upper()] for i in x]},
            "hv autorecovery": {"command":"spc 69", "topics":("parameters/high-voltage/mode",), "transform":lambda s,x:[s.hv_enable[i.upper()] for i in x]},
            "hv jumpstart": {"command":"spc 57", "topics":("parameters/high-voltage/jumpstart",), "transform":lambda s,x:[True if i == "YES" else False for i in x]},
        }

        self.set_commands = {
            "start pump": {"command":"spc 37", "read_value":True, "read_command":"is pump on", "transform":lambda s,x:x},
            "stop pump": {"command":"spc 38", "read_value":True, "read_command":"is pump on", "transform":lambda s,x:x},
            "initiate hipot": {"command":"spc 52", "read_value":False},
            "setpoint": {"command":"spc 3D", "read_value":True, "read_command":"setpoint", "transform":lambda s,x:x},
            "pump size": {"command":"spc 12", "read_value":True, "read_command":"pump size", "transform":lambda s,x:x},
            "calibration factor": {"command":"spc 1E", "read_value":True, "read_command":"calibration factor", "transform":lambda s,x:x},
            "target voltage": {"command":"spc 53", "read_value":True, "read_command":"target voltage", "transform":lambda s,x:x},
            "foldback enable": {"command":"spc 56", "read_value":True, "read_command":"foldback enable", "transform":lambda s,x:["YES" if i else "NO" for i in x]},
            "foldback voltage": {"command":"spc 54", "read_value":True, "read_command":"foldback voltage", "transform":lambda s,x:x},
            "foldback pressure": {"command":"spc 55", "read_value":True, "read_command":"foldback pressure", "transform":lambda s,x:x},
            "pressure unit": {"command":"spc 0E", "read_value":False, "transform":lambda s,x:x},
            "auto restart": {"command":"spc 33", "read_value":True, "read_command":"auto restart", "transform":lambda s,x:[s.auto_restart[i.upper()] for i in x]},
            "hv autorecovery": {"command":"spc 68", "read_value":True, "read_command":"hv autorecovery", "transform":lambda s,x:[s.hv_enable[i.upper()] for i in x]},
            "hv jumpstart": {"command":"spc 57", "read_value":True, "read_command":"hv jumpstart", "transform":lambda s,x:["YES" if i else "NO" for i in x]},
        }

    def init_after(self):
        """
        Constructor of the class.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.connect()
        
    def connect(self):
        """
        This function is used to connect to the device and start all threads.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        try:
            self.connection = telnetPackage.ConnectionClass(devisor=self.devisor, address=self.address)
        except:
            return

        
        # Initial read
        self.set("pressure unit", ["M"]) # Set pressure unit
        self.get_all_parameters()

        # Start threads
        self.stopThreads = False
        self.loopReader = Thread(target = self.read_loop)
        self.loopReader.start()

    def disconnect(self):
        """
        This function is used to stop all threads and disconnect from the device.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.stopThreads = True

        try:
            self.connection.close()
        except:
            return
        
    def set(self, command_name, data=[]):
        """
        Function is used to set single value to Gamma Ion Vacuum Pump Controller device.

        Parameters:
        command_name (string): name of the command
        data (list): list of all the data that needs to be sent

        Returns:
        No returns
        """

        data = [str(i) for i in self.set_commands[command_name]["transform"](self, data)]
        response = self.connection.ask(f"{self.set_commands[command_name]['command']}{' '+','.join(data) if len(data) > 0 else ''}").strip(">")
        
        if response[0:2] == "OK":

            if command_name == "stop pump":
                time.sleep(0.1)

            if self.set_commands[command_name]["read_value"]:
                self.get(self.set_commands[command_name]["read_command"])

        else:
            response_list = response.split(" ", 2)

            error_code = response_list[1]
            error = re.match("\*ERROR:\s+(?P<desc>.*)", response_list[2])["desc"]
            self.dev.log.new_log(f"Error reading \"{command_name}\" with error code {error_code}: {error}.", "WARNING")
        
            if self.set_commands[command_name]["read_value"]:
                self.get(self.set_commands[command_name]["read_command"])

    def get(self, command_name):
        """
        Function is used to read single value from Gamma Ion Vacuum Pump Controller device.

        Parameters:
        command_name (string): name of the command

        Returns:
        No returns
        """

        response = self.connection.ask(self.get_commands[command_name]["command"]).strip(">")
        
        if response[0:2] == "OK":

            if command_name == "supply status":
                response_list = response.split(" ", 2)
            else:
                response_list = response.split(" ")

            data = self.get_commands[command_name]["transform"](self, response_list[2].split(","))

            for value, topic in zip(data, self.get_commands[command_name]["topics"]):
                if topic == "":
                    continue
                self.params[topic].publish_value(value)

        else:
            response_list = response.split(" ", 2)

            error_code = response_list[1]
            error = re.match("\*ERROR:\s+(?P<desc>.*)", response_list[2])["desc"]
            self.dev.log.new_log(f"Error reading \"{command_name}\" with error code {error_code}: {error}.", "WARNING")
            

    def get_all_parameters(self):
        """
        Function is used to read all values from Gamma Ion Vacuum Pump Controller device.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        # Read all
        self.get("supply status") # pump status
        self.get("is pump on") # is high voltage enabled
        self.get("auto restart") # auto restart settings
        self.get("hv autorecovery") # autorecovery settings
        self.get("current") # current
        self.get("pressure") # pressure
        self.get("voltage") # voltage
        self.get("pump size") # pump size
        #self.get("calibration factor") # calibration factor # COMMAND NOT WORKING/DON'T KNOW HOW TO USE IT
        self.get("setpoint") # setpoint
        self.get("target voltage") # target voltage
        self.get("foldback enable") # foldback status
        self.get("foldback voltage") # foldback voltage
        self.get("foldback pressure") # foldback pressure
        self.get("hv jumpstart") # jumpstart status

    def read_loop(self):
        """
        Function is used to read parameters and status from Gamma Ion Vacuum Pump Controller device.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        last_reading = time.time()-float(self.params['control/read-interval'].value)
        while not self.stopThreads and float(self.params['control/read-interval'].value) > 1e-5:

            if time.time()-last_reading > float(self.params['control/read-interval'].value):
                self.get_all_parameters()

                last_reading = time.time()
            
            time.sleep(0.1)


    def exit_pre(self):
        """
        This function is used to join all threads and close serial port.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.disconnect()