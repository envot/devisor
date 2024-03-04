import serial
from threading import Thread
import time

from devisor.devisorbase import DeviceBase, devisor_import


initNodes = {}

# Pressure node
def read_now(pB):
    """
    Function is used to handle read-now button.

    Parameters:
    pB

    Returns:
    No returns
    """

    pB.dev.read_pressure()
    pB.dev.params['pressure/read-now'].publish_value(False)


pressure = {}

pressure['read-now'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : read_now,
}

pressure['refresh-rate'] = {
    'valueInit' : 60,
    'settable' : True,
    'unit' : 's',
}

pressure['cnv1'] = {
    'valueInit' : '',
    'settable' : False,
    'unit' : 'mbar',
}

pressure['img1'] = {
    'valueInit' : '',
    'settable' : False,
    'unit' : 'mbar',
}

initNodes['pressure'] = pressure


class DeviceClass(DeviceBase):
    """
    This class is used to communicate with Agilent XGS-600 device over the serial port.
    """

    def init_pre(self, port_name="/dev/ttyUSB1"):
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

        # All implemented commands
        self.commands = {"read_pressure_3":"#0002UIMG1",
                         "read_pressure_dump":"#000F",
                         "read_pressure_units":"#0013",
                         "set_pressure_units_torr":"#0010",
                         "set_pressure_units_mbar":"#0011",
                         "set_pressure_units_pascal":"#0012",
                         "test":"#0001"}

        # Commands that need processing
        self.responses = {"read_pressure_3": lambda x: float(x),
                          "read_pressure_dump": lambda x: [i.strip() if i.strip()=="OPEN" else float(i) for i in x.split(",")],
                          "read_pressure_units": lambda x: {"00":"Torr", "01":"mBar", "02":"Pascal"}[x]}

        # Open serial port
        self.open_serial()

        # Start threads
        self.threadsStop = False
        self.pressureReader = Thread(target = self.read_loop)
        self.pressureReader.start()


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

        self.serial_port.close()

    def write_read_serial(self, command_name):
        """
        Function is used to write, read and process messages. It sends command with given "command_name"
        and waits for response. In the end the function processes received message.

        Parameters:
        command_name (string): name of the command from dictionary "commands"

        Returns:
        (multiple data types): processed message or some kind of error
        """

        # Check if command name exist
        if command_name not in self.commands: # No such command
            return "No such command"

        # Write command
        bytes_sent = self.serial_port.write(f"{self.commands[command_name]}\r".encode())

        if bytes_sent == 0:
            return "Write timeout"


        # Read response
        next_message = self.serial_port.read_until(expected=b'\r').decode().strip()

        if next_message == "":
            return "Read timeout"

        # Process message
        try:
            if next_message.startswith("?FF"):
                return "Error"
            elif next_message == ">":
                return ""
            elif command_name in self.responses.keys():
                return self.responses[command_name](next_message[1:])
            else:
                return next_message[1:]
        except:
            self.dev.log.new_log(f"Unable to process message.", 'ERROR')

    def read_loop(self):
        """
        This function is used to periodically read from Agilent XGS-600 device.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        # Set pressure units to mbar
        self.write_read_serial("set_pressure_units_mbar")

        # Read pressure
        last_reading_time = time.time()-float(self.dev.params['pressure/refresh-rate'].value)
        while not self.threadsStop:

            if self.dev.params['pressure/read-now'].value:
                last_reading_time = time.time()

            elif time.time()-last_reading_time > float(self.dev.params['pressure/refresh-rate'].value):
                last_reading_time = time.time()
                self.read_pressure()
                

    def read_pressure(self):
        """
        This function is used to read pressure from the Agilent XGS-600 device.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        pressure = self.write_read_serial("read_pressure_dump")

        try:
            if len(pressure) < 3:
                self.dev.log.new_log(f"Incomplete pressure dump.", 'WARNING')
            else:
                self.dev.params['pressure/cnv1'].publish_value(pressure[0])
                self.dev.params['pressure/img1'].publish_value(pressure[2])
        except:
            self.dev.log.new_log(f"Pressure dump reading failed.", 'WARNING')

    def exit_pre(self):
        """
        This function is used to join all threads and close serial port.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.threadsStop = True
        self.pressureReader.join()
        self.close_serial()


        