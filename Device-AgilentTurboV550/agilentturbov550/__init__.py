import serial
from threading import Thread
import time

from devisor.devisorbase import DeviceBase


initNodes = {}

# Control node
def start_stop_handle(pB):
    """
    Function is used to handle "start-stop" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/start-stop'].value:
        pB.dev.send_command("A")

    else:
        pB.dev.send_command("B")

def low_speed_handle(pB):
    """
    Function is used to handle "low-speed" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/low-speed'].value:
        pB.dev.send_command("C")

    else:
        pB.dev.send_command("D")

def op_params_handle(pB):
    """
    Function is used to handle "get-operational-params" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/get-operational-params'].value:
        pB.dev.send_command("E")
        time.sleep(0.05)
        pB.dev.params['control/get-operational-params'].publish_value(False)

def pump_times_zeroing_handle(pB):
    """
    Function is used to handle "pump-times-zeroing" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/pump-times-zeroing'].value:
        pB.dev.send_command("F")
        time.sleep(0.05)
        pB.dev.params['control/pump-times-zeroing'].publish_value(False)

def read_params_handle(pB):
    """
    Function is used to handle "read-params" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/read-params'].value:
        pB.dev.send_command("G")
        time.sleep(0.05)
        pB.dev.params['control/read-params'].publish_value(False)

def write_params_handle(pB):
    """
    Function is used to handle "write-params" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/write-params'].value:
        response = pB.dev.send_command("H")
        time.sleep(0.05)
        pB.dev.params['control/write-params'].publish_value(False)

        if response:
            pB.dev.send_command("G")
            

def get_operating_status_handle(pB):
    """
    Function is used to handle "get-operating-status" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/get-operating-status'].value:
        pB.dev.send_command("I")
        time.sleep(0.05)
        pB.dev.params['control/get-operating-status'].publish_value(False)    

def get_numerical_reading_handle(pB):
    """
    Function is used to handle "get-numerical-reading" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/get-numerical-reading'].value:
        pB.dev.send_command("J")
        time.sleep(0.05)
        pB.dev.params['control/get-numerical-reading'].publish_value(False)

def get_counters_reading_handle(pB):
    """
    Function is used to handle "get-counters-reading" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/get-counters-reading'].value:
        pB.dev.send_command("K")
        time.sleep(0.05)
        pB.dev.params['control/get-counters-reading'].publish_value(False)

def front_panel_operation_handle(pB):
    """
    Function is used to handle "front-panel-operation" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/front-panel-operation'].value:
        response = pB.dev.send_command("P")
        time.sleep(0.05)
        pB.dev.params['control/front-panel-operation'].publish_value(False)

        if response:
            pB.dev.params['control/operation-mode'].publish_value("Front panel")

def remote_operation_handle(pB):
    """
    Function is used to handle "remote-operation" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/remote-operation'].value:
        response = pB.dev.send_command("Q")
        time.sleep(0.05)
        pB.dev.params['control/remote-operation'].publish_value(False)

        if response:
            pB.dev.params['control/operation-mode'].publish_value("Remote")

def rs232_operation_handle(pB):
    """
    Function is used to handle "rs232-operation" node activation.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params['control/rs232-operation'].value:
        response = pB.dev.send_command("R")
        time.sleep(0.05)
        pB.dev.params['control/rs232-operation'].publish_value(False)

        if response:
            pB.dev.params['control/operation-mode'].publish_value("RS232")


control = {}

control['operation-mode'] = {
    'valueInit' : "Front panel",
    'settable' : False,
}

control['start-stop'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : start_stop_handle,
}

control['low-speed'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : low_speed_handle,
}

control['get-operational-params'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : op_params_handle,
}

control['pump-times-zeroing'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : pump_times_zeroing_handle,
}

control['read-params'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : read_params_handle,
}

control['write-params'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : write_params_handle,
}

control['write-params/speed-adjust'] = {
    'valueInit' : "",
    'settable' : True,
    'unit' : 'KRMP'
}

control['write-params/speed-threshold'] = {
    'valueInit' : "",
    'settable' : True,
}

control['write-params/run-up-time'] = {
    'valueInit' : "",
    'settable' : True,
    'unit' : 's',
}

control['write-params/deat-time'] = {
    'valueInit' : "NO",
    'format' : ['NO', 'YES'],
    'settable' : True,
    'datatype' : 'enum',
}

control['write-params/soft-start-mode'] = {
    'valueInit' : "NO",
    'format' : ['NO', 'YES'],
    'settable' : True,
    'datatype' : 'enum',
}

control['write-params/water-cooling'] = {
    'valueInit' : "NO",
    'format' : ['NO', 'YES'],
    'settable' : True,
    'datatype' : 'enum',
}

control['get-operating-status'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : get_operating_status_handle,
}

control['get-numerical-reading'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : get_numerical_reading_handle,
}

control['get-counters-reading'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : get_counters_reading_handle,
}

control['front-panel-operation'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : front_panel_operation_handle,
}

control['remote-operation'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : remote_operation_handle,
}

control['rs232-operation'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : rs232_operation_handle,
}

initNodes['control'] = control

# Status node
status = {}

status['operating-status'] = {
    'valueInit' : "",
    'settable' : False,
}

status['r1-status'] = {
    'valueInit' : "",
    'settable' : False,
}

status['r2-status'] = {
    'valueInit' : "",
    'settable' : False,
}

initNodes['status'] = status

# Parameters node
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


parameters = {}

parameters['read-interval'] = {
    'valueInit' : 0.0,
    'settable' : False,
    'broker_func' : read_interval_handle,
    'unit' : 's'
}

parameters['current'] = {
    'valueInit' : 0.0,
    'settable' : False,
    'unit' : 'A'
}

parameters['voltage'] = {
    'valueInit' : 0.0,
    'settable' : False,
    'unit' : 'V'
}

parameters['frequency'] = {
    'valueInit' : 0,
    'settable' : False,
    'unit' : 'Hz'
}

parameters['rotational-speed'] = {
    'valueInit' : 0,
    'settable' : False,
    'unit' : 'KRPM'
}

parameters['pump-temperature'] = {
    'valueInit' : 0,
    'settable' : False,
    'unit' : '°C'
}

parameters['cycle-time'] = {
    'valueInit' : 0,
    'settable' : False,
}

parameters['pump-life'] = {
    'valueInit' : 0,
    'settable' : False,
    'unit' : 'h',
}

parameters['cycle-number'] = {
    'valueInit' : 0,
    'settable' : False,
}

parameters['speed-adjust'] = {
    'valueInit' : 0,
    'settable' : False,
    'unit' : 'KRPM'
}

parameters['speed-threshold'] = {
    'valueInit' : 0,
    'settable' : False,
    'unit' : 'KRPM',
}

parameters['run-up-time'] = {
    'valueInit' : 0,
    'settable' : False,
    'unit' : 's'
}

parameters['deat-time'] = {
    'valueInit' : "NO",
    'settable' : False,
}

parameters['soft-start-mode'] = {
    'valueInit' : "NO",
    'settable' : False,
}

parameters['water-cooling'] = {
    'valueInit' : "NO",
    'settable' : False,
}

initNodes['parameters'] = parameters



class DeviceClass(DeviceBase):
    """
    This class is used to communicate with Agilent Turbo-V 550 over the serial port.
    """

    def init_pre(self, port_name="/dev/ttyUSB0"):
        """
        Constructor of the class.

        Parameters:
        port_name (string): name of the serial port

        Returns:
        No returns
        """

        self.initNodes = initNodes
        self.read_timeout = 5
        self.write_timeout = 5
        self.port_name = port_name
        self.serial_port = None
        self.deviceAvailable = True
        self.stopThreads = False

        # Dictionaries
        self.yes_no_dict = {0:"NO", 1:"YES", "NO":0, "YES":1}
        self.baud_dict = {0:600, 1:1200, 2:2400, 3:4800, 4:9600, 600:0, 1200:1, 2400:2, 4800:3, 9600:4}
        self.status_dict = {0:"STOP", 1:"WAITING INTERLOCK", 2:"STARTING", 3:"NORMAL OPERATION", \
                               4:"HIGH LOAD", 5:"\"    \"", 6:"FAILURE", 7:"APPROACHING LOW SPEED"}
        self.read_size = {"A":2, "B":2, "C":2, "D":2, "E":22, "F":2, "G":12, "H":2, "I":2, \
                          "J":5, "K":11, "L":12, "N":2, "O":2, "P":2, "Q":2, "R":2, "S":2}

        # Open serial port
        self.open_serial()

    def init_after(self):
        """
        Function initializes this class after MQTT nodes have been initialized.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        # Read status and parameters
        self.send_command("E")
        self.send_command("G")
        self.send_command("J")

    def open_serial(self):
        """
        Function is used to create and open new serial port.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.serial_port = serial.Serial(port=self.port_name, 
                                         baudrate=9600, 
                                         timeout=self.read_timeout,
                                         write_timeout=self.write_timeout,
                                         parity=serial.PARITY_NONE,
                                         stopbits=serial.STOPBITS_ONE,
                                         bytesize=serial.EIGHTBITS)

        if not self.serial_port.is_open:
            self.serial_port.open()

        self.serial_port.reset_output_buffer()
        self.serial_port.reset_input_buffer()

    def close_serial(self):
        """
        Function is used to close serial port.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.stopThreads = True
        self.serial_port.close()

    def write(self, command_name):
        """
        Function is used to write commands to the serial port.

        Parameters:
        command_name (string): name of the command to send

        Returns:
        No returns
        """

        # Get data
        message_bytes = command_name.encode('ISO-8859-1')
        if command_name == "S":
            message_bytes += self.baud_dict[self.params['control/set-baud-rate/baud-rate'].value].to_bytes(1, byteorder = 'little')
        elif command_name == "H":

            if 0 <= self.params['control/write-params/speed-adjust'].value <= 256 and \
               0 <= self.params['control/write-params/speed-threshold'].value <= 256 and \
               0 <= self.params['control/write-params/run-up-time'].value <= 2**32 and \
               self.params['control/write-params/deat-time'].value.upper() in self.yes_no_dict.keys() and \
               self.params['control/write-params/soft-start-mode'].value.upper() in self.yes_no_dict.keys() and \
               self.params['control/write-params/water-cooling'].value.upper() in self.yes_no_dict.keys():

                message_bytes += (self.params['control/write-params/speed-adjust'].value).to_bytes(1, byteorder = 'little')
                message_bytes += (self.params['control/write-params/speed-threshold'].value).to_bytes(1, byteorder = 'little')
                message_bytes += (self.params['control/write-params/run-up-time'].value).to_bytes(4, byteorder = 'little')
                message_bytes += self.yes_no_dict[self.params['control/write-params/deat-time'].value].to_bytes(1, byteorder = 'little')
                message_bytes += self.yes_no_dict[self.params['control/write-params/soft-start-mode'].value].to_bytes(1, byteorder = 'little')
                message_bytes += self.yes_no_dict[self.params['control/write-params/water-cooling'].value].to_bytes(1, byteorder = 'little')

            else:
                self.dev.new_log.log("Parameter out of range", "WARNING")

        # Calculate CRC
        crc = (0xFF + 1 - (sum(i for i in (message_bytes if len(message_bytes) == 1 else message_bytes[:-1])) & 0xFF)).to_bytes(1, byteorder = 'little')

        # Write command
        bytes_sent = self.serial_port.write(message_bytes+crc)

        if bytes_sent == 0:
            self.dev.log.new_log("Write timeout", "WARNING")
            return 0
        
        return bytes_sent
    
    def read(self, command_name):
        """
        Function is used to read commands to the serial port.

        Parameters:
        command_name (string): name of the command to read

        Returns:
        No returns
        """

        # Read response
        response = self.serial_port.read(size=self.read_size[command_name])

        if response == "":
            self.dev.log.new_log("Read timeout", "WARNING")
            return False

        # Decode response
        try:

            if command_name in ["A", "B", "C", "D", "F", "N", "O", "P", "Q", "R", "H"]:
                return ord(response[0:1].decode('ISO-8859-1')) == 0x06
            
            elif command_name == "E":
                self.dev.params['status/operating-status'].publish_value(self.status_dict[int.from_bytes(response[0:1], byteorder="little") & 0b00000111])
                self.params['parameters/cycle-time'].publish_value(int.from_bytes(response[1:5], byteorder="little"))
                self.params['parameters/pump-life'].publish_value(int.from_bytes(response[5:9], byteorder="little"))
                self.params['parameters/pump-temperature'].publish_value(int.from_bytes(response[9:11], byteorder="little"))
                self.params['parameters/current'].publish_value(int.from_bytes(response[11:12], byteorder="little")/255*10)
                self.params['parameters/voltage'].publish_value(int.from_bytes(response[12:13], byteorder="little")/255*100)
                self.params['parameters/frequency'].publish_value(int.from_bytes(response[13:17], byteorder="little"))
                self.params['parameters/cycle-number'].publish_value(int.from_bytes(response[17:19], byteorder="little"))

                r1_byte = int.from_bytes(response[19:20], byteorder="little")
                r2_byte = int.from_bytes(response[20:21], byteorder="little")
                self.params['status/r1-status'].publish_value("OFF" if r1_byte & 0b00100000 == 0 else self.status_dict[r1_byte & 0b00000111])
                self.params['status/r2-status'].publish_value("OFF" if r2_byte & 0b01000000 == 0 else self.status_dict[r2_byte & 0b00000111])

            elif command_name == "G":
                self.params['parameters/speed-adjust'].publish_value(int.from_bytes(response[0:1], byteorder="little"))
                self.params['control/write-params/speed-adjust'].publish_value(int.from_bytes(response[0:1], byteorder="little"))
                self.params['parameters/cycle-number'].publish_value(int.from_bytes(response[1:3], byteorder="little"))
                self.params['parameters/speed-threshold'].publish_value(int.from_bytes(response[3:4], byteorder="little"))
                self.params['control/write-params/speed-threshold'].publish_value(int.from_bytes(response[3:4], byteorder="little"))
                self.params['parameters/run-up-time'].publish_value(int.from_bytes(response[4:8], byteorder="little"))
                self.params['control/write-params/run-up-time'].publish_value(int.from_bytes(response[4:8], byteorder="little"))
                self.params['parameters/deat-time'].publish_value(self.yes_no_dict[int.from_bytes(response[8:9], byteorder="little")])
                self.params['control/write-params/deat-time'].publish_value(self.yes_no_dict[int.from_bytes(response[8:9], byteorder="little")])
                self.params['parameters/soft-start-mode'].publish_value(self.yes_no_dict[int.from_bytes(response[9:10], byteorder="little")])
                self.params['control/write-params/soft-start-mode'].publish_value(self.yes_no_dict[int.from_bytes(response[9:10], byteorder="little")])
                self.params['parameters/water-cooling'].publish_value(self.yes_no_dict[int.from_bytes(response[10:11], byteorder="little")]) 
                self.params['control/write-params/water-cooling'].publish_value(self.yes_no_dict[int.from_bytes(response[10:11], byteorder="little")])            

            elif command_name == "I":
                self.params['status/operating-status'].publish_value(self.status_dict[int.from_bytes(response[0:1], byteorder="little") & 0b00000111])

            elif command_name == "J":
                self.params['parameters/current'].publish_value(int.from_bytes(response[0:1], byteorder="little")/255*10)
                self.params['parameters/voltage'].publish_value(int.from_bytes(response[1:2], byteorder="little")/255*100)
                self.params['parameters/rotational-speed'].publish_value(int.from_bytes(response[2:3], byteorder="little"))
                self.params['parameters/pump-temperature'].publish_value(int.from_bytes(response[3:4], byteorder="little"))

            elif command_name == "K":
                self.params['parameters/cycle-time'].publish_value(int.from_bytes(response[0:4], byteorder="little"))
                self.params['parameters/pump-life'].publish_value(int.from_bytes(response[4:8], byteorder="little"))
                self.params['parameters/cycle-number'].publish_value(int.from_bytes(response[8:10], byteorder="little"))

            elif command_name == "L":
                self.params['parameters/software-version'].publish_value(int.from_bytes(response[0:3], byteorder="little"))

            elif command_name == "S":
                self.params['parameters/baud-rate'].publish_value(self.baud_dict[int.from_bytes(response[0:1], byteorder="little")])

            return True

        except:
            return False
        
    def send_command(self, command_name):
        """
        Function is used to send the command to Agilent Turbo-V 550 device and read its response.

        Parameters:
        command_name (string): name of the command to send

        Returns:
        No returns
        """

        self.deviceAvailable = False

        # Write command
        bytes_sent = self.write(command_name)

        if bytes_sent == 0:
            return False

        # Read response
        response = self.read(command_name)
    
        self.deviceAvailable = True

        return response
    
    def read_loop(self):
        """
        Function is used to read parameters and status from Agilent Turbo-V 550 device continuously.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        last_reading = time.time()-float(self.params['parameters/read-interval'].value)
        while float(self.params['parameters/read-interval'].value) > 1e-5 and not self.stopThreads:

            if self.deviceAvailable and time.time()-last_reading > float(self.params['parameters/read-interval'].value):
                self.send_command("E")
                self.send_command("G")
                self.send_command("J")
                last_reading = time.time()

    def exit_pre(self):
        """
        This function is used to close serial port.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.close_serial()