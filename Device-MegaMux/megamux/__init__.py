from smbus2 import SMBus
from threading import Thread
import time
import re

from devisor.devisorbase import DeviceBase, devisor_import

MCP_DICT = {
    'IODIRA' : 0x00, # IODIR: I/O DIRECTION REGISTER
    'IODIRB' : 0x01,
    'IPOLA' : 0x02, # IPOL: INPUT POLARITY PORT REGISTER
    'IPOLB' : 0x03,
    'GPINTENA' : 0x04, # GPINTEN: INTERRUPT-ON-CHANGE PINS
    'GPINTENB' : 0x05,
    'DEFVALA' : 0x06, # DEFVAL: DEFAULT VALUE REGISTER
    'DEFVALB' : 0x07,
    'INTCONA' : 0x08, # INTCON: INTERRUPT-ON-CHANGE CONTROL REGISTER
    'INTCONB' : 0x09,
    'IOCON' : 0x0A, # IOCON: I/O EXPANDER CONFIGURATION REGISTER 
    #'IOCON' : 0x0B,
    'GPPUA' : 0x0C, # GPPU: GPIO PULL-UP RESISTOR REGISTER 
    'GPPUB' : 0x0D,
    'INTFA' : 0x0E, # INTF: INTERRUPT FLAG REGISTER 
    'INTFB' : 0x0F,
    'INTCAPA' : 0x10, # INTCAP: INTERRUPT CAPTURED VALUE FOR PORT REGISTER
    'INTCAPB' : 0x11,
    'GPIOA' : 0x12, # GPIO: GENERAL PURPOSE I/O PORT REGISTER 
    'GPIOB' : 0x13,
    'OLATA' : 0x14, # OLAT: OUTPUT LATCH REGISTER 0
    'OLATB' : 0x15,
}

CHANNEL_MAPPING = {
    "None": {"address":0b00000000},
    "1": {"address":0b00000001, "bank":"A"},
    "2": {"address":0b00000011, "bank":"A"},
    "3": {"address":0b00000101, "bank":"A"},
    "4": {"address":0b00000111, "bank":"A"},
    "5": {"address":0b00001001, "bank":"A"},
    "6": {"address":0b00001011, "bank":"A"},
    "7": {"address":0b00001101, "bank":"A"},
    "8": {"address":0b00001111, "bank":"A"},
    "9": {"address":0b00010000, "bank":"A"},
    "10": {"address":0b00110000, "bank":"A"},
    "11": {"address":0b01010000, "bank":"A"},
    "12": {"address":0b01110000, "bank":"A"},
    "14": {"address":0b10010000, "bank":"A"},
    "15": {"address":0b10110000, "bank":"A"},
    "16": {"address":0b11010000, "bank":"A"},
    "17": {"address":0b11110000, "bank":"A"},
    "18": {"address":0b00000001, "bank":"B"},
    "19": {"address":0b00000011, "bank":"B"},
    "20": {"address":0b00000101, "bank":"B"},
    "21": {"address":0b00000111, "bank":"B"},
    "22": {"address":0b00001001, "bank":"B"},
    "23": {"address":0b00001011, "bank":"B"},
    "24": {"address":0b00001101, "bank":"B"},
    "25": {"address":0b00001111, "bank":"B"}
}

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
    pB.dev.connect()


control = {}

control['reconnect'] = {
    'valueInit' : False,
    'broker_func' : reconnect_handle,
    'datatype' : 'boolean',
    'brokerInit' : False,
    'settable' : True,
}

control['switchedN'] = {
    'valueInit' : False,
    'brokerInit' : False,
    'settable' : True,
}

control['switchedP'] = {
    'valueInit' : False,
    'brokerInit' : False,
    'settable' : True,
}

initNodes['control'] = control

# Channels node
for i in range(4):

    board = {}

    board['outN'] = {
        'valueInit' : "None",
        'format' : ["None","1","2","3","4","5","6","7","8","9","10","11","12","14","15","16","17","18","19","20","21","22","23","24","25"],
        'broker_func' : lambda pB: pB.dev.select("N", int(re.match("(?P<i>\d)/.*?", pB.param)['i'])),
        'datatype' : 'enum',
        'brokerInit' : False,
        'settable' : True,
    }

    board['outP'] = {
        'valueInit' : "None",
        'format' : ["None","1","2","3","4","5","6","7","8","9","10","11","12","14","15","16","17","18","19","20","21","22","23","24","25"],
        'broker_func' : lambda pB: pB.dev.select("P", int(re.match("(?P<i>\d)/.*?", pB.param)['i'])),
        'datatype' : 'enum',
        'brokerInit' : False,
        'settable' : True,
    }

    initNodes[str(i)] = board



class DeviceClass(DeviceBase):
    """
    Class is used to communicate with MegaMux device using I2C protocol.
    """

    def init_pre(self, mcpN=[0x20, 0x22, 0x24, 0x26], mcpP=[0x21, 0x23, 0x25, 0x27]):
        """
        This function is used to initialize parameters and connect to the device.

        Parameters:
        mcpN (list): addresses of N side MCP23017
        mcpP (list): addresses of P side MCP23017

        Returns:
        No returns
        """

        self.initNodes = initNodes
        self.boards = ["0", "1", "2", "3"]
        self.mcps = {"N":tuple(mcpN), "P":tuple(mcpP)} # MCP23017 addresses

    def init_after(self):
        """
        This function is used to initialize after initializing nodes.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.connect()

    def connect(self):
        """
        This function is used to initialize I2C communication.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        # Open I2C bus and configure GPIO pins to output
        try:
            self.i2c = SMBus(1)
            self.configure_gpio()
        except Exception as e:
            self.dev.log.new_log(f"Connection failed with exception: {e}", 'WARNING')
            return
    
    def configure_gpio(self):
        """
        Function is used to configure GPIO pins of MCP23017 as output.

        Parameters:
        No parameters

        Return:
        No return
        """

        for board in range(4):
            self.select("N", str(board))
            self.select("P", str(board))

        for mcpN, mcpP in zip(self.mcps["N"], self.mcps["P"]):

            # Set GPIO to output
            self.i2c.write_byte_data(mcpN, MCP_DICT['IODIRA'], 0b00000000)
            self.i2c.write_byte_data(mcpN, MCP_DICT['IODIRB'], 0b00000000)
            self.i2c.write_byte_data(mcpP, MCP_DICT['IODIRA'], 0b00000000)
            self.i2c.write_byte_data(mcpP, MCP_DICT['IODIRB'], 0b00000000)

    def select(self, side, board):
        """
        Function is used to connect selected pins to the MegaMux outputs.

        Parameters:
        No parameters

        Return:
        No return
        """

        # Check side
        if side not in ["P", "N"]:
            self.dev.log.new_log("Board side should be N or P.", 'WARNING')
            return 
        
        # Check board
        if str(board) not in self.boards:
            self.dev.log.new_log("Board number should be 0, 1, 2 or 3.", 'WARNING')
            return 
        
        # Check channel
        try:
            out = self.dev.params[f"{board}/out{side}"].value
            if out not in CHANNEL_MAPPING.keys():
                self.dev.log.new_log("Channel number must be 1-25 except 13 or 'None'.", 'WARNING')
                return
        except:
            self.dev.log.new_log("Channel number must be 1-25 except 13 or 'None'.", 'WARNING')
            return
        
        
        # Connect respective channels to output
        try:

            # Disconnect all channels
            for b in range(4):
                self.i2c.write_byte_data(self.mcps[side][b], MCP_DICT[f"GPIOA"], CHANNEL_MAPPING["None"]['address'])
                self.i2c.write_byte_data(self.mcps[side][b], MCP_DICT[f"GPIOB"], CHANNEL_MAPPING["None"]['address'])

                if out == "None" or b != board:
                    self.dev.params[f"{b}/out{side}"].publish_value("None")

            # Connect channel
            if out != "None":
                self.i2c.write_byte_data(self.mcps[side][board], 
                                         MCP_DICT[f"GPIO{CHANNEL_MAPPING[out]['bank']}"], 
                                         CHANNEL_MAPPING[out]['address'])
                self.dev.params[f"control/switched{side}"].publish_value(True)
                
        except Exception as e:
            self.dev.log.new_log(f"Setting channel failed with exception: {e}", 'WARNING')
            return

    def exit_pre(self):
        """
        This function is used to close I2C communication.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        self.i2c.close()