from threading import Thread
import time
import re

from devisor.devisorbase import DeviceBase, devisor_import

scpiPackage = devisor_import(None, 'scpi', 'connection')


initNodes = {}

# Channel nodes
def enable_channel(pB):
    """
    Function is used to enable/disable certain channel.

    Parameters:
    pB : parameter base
    ch (int): channel number

    Returns:
    No returns
    """

    ch = int(re.match("[^\/]+/(?P<ch>\d)/.*?", pB.param)['ch'])

    # Not detected
    if not pB.dev.params[f'channels/{ch}/detected'].value:
        pB.dev.log.new_log("Channel not detected.", "WARNING")
        pB.dev.params[f'channels/{ch}/enable'].publish_value(False)
        return

    # Enable/disable    
    if pB.dev.params[f'channels/{ch}/enable'].value:
        response = pB.dev.connection.ask(f"chan:enab {ch}").strip("\r")

        if response != "OK":
            pB.dev.log.new_log(f"Enabling channel {ch} failed: {response}", "WARNING")
            pB.dev.params[f'channels/{ch}/enable'].publish_value(False)
            return

    else:
        response = pB.dev.connection.ask(f"chan:disab {ch}").strip("\r")

        if response != "OK":
            pB.dev.log.new_log(f"Disabling channel {ch} failed: {response}", "WARNING")
            pB.dev.params[f'channels/{ch}/enable'].publish_value(True)
            return

def enable_all_channels(pB):
    """
    Function is used to enable all channels.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params[f'general/enable-all'].value:
        response = pB.dev.connection.ask(f"chan:enab all").strip("\r")

        if response != "OK":
            pB.dev.log.new_log(f"Enabling all channels failed: {response}", "WARNING")
            pB.dev.params[f'general/enable-all'].publish_value(False)
            return

        for ch in range(8):
            pB.dev.params[f'channels/{ch}/enable'].publish_value(True)
        
        pB.dev.params[f'general/enable-all'].publish_value(False)

def disable_all_channels(pB):
    """
    Function is used to disable all channels.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    pB.dev.log.new_log("Disable all command not working at the moment.", "INFO")

    # Cannot disable all channels at once apparently
    if pB.dev.params[f'general/disable-all'].value:
        # response = pB.dev.connection.ask(f"chan:disab all").strip("\r")

        # if response != "OK":
        #     pB.dev.log.new_log(f"Disabling all channels failed.", "WARNING")
        #     pB.dev.params[f'general/disable-all'].publish_value(False)
        #     return

        # for ch in range(8):
        #     pB.dev.params[f'channels/{ch}/enable'].publish_value(False)

        pB.dev.params[f'general/disable-all'].publish_value(False)

def reset_interlock(pB):
    """
    Function is used to reset interlock of a certain channel.

    Parameters:
    pB : parameter base
    ch (int): channel number

    Returns:
    No returns
    """

    ch = int(re.match("[^\/]+/(?P<ch>\d)/.*?", pB.param)['ch'])

    # Not detected
    if not pB.dev.params[f'channels/{ch}/detected'].value:
        pB.dev.log.new_log("Channel not detected.", "WARNING")
        pB.dev.params[f'channels/{ch}/reset'].publish_value(False)
        return

    # Reset
    if pB.dev.params[f'channels/{ch}/reset'].value:
        response = pB.dev.connection.ask(f"int:cle {ch}").strip("\r")

        if response != "OK":
            pB.dev.log.new_log(f"Reset channel {ch} failed: {response}", "WARNING")

        pB.dev.params[f'channels/{ch}/reset'].publish_value(False)

def reset_all_interlocks(pB):
    """
    Function is used to reset interlocks of all channels.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    if pB.dev.params[f'general/reset-all'].value:
        response = pB.dev.connection.ask(f"int:cle all").strip("\r")

        if response != "OK":
            pB.dev.log.new_log(f"Reset all channels failed: {response}", "WARNING")

        pB.dev.params[f'general/reset-all'].publish_value(False)

def read_interval(pB):
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

def max_power(pB):
    """
    Function is used to set power threshold.

    Parameters:
    pB : parameter base

    Returns:
    No returns
    """

    ch = int(re.match("[^\/]+/(?P<ch>\d)/.*?", pB.param)['ch'])

    if 0 < float(pB.dev.params[f'channels/{ch}/max-power/set-max-power'].value) < 38:
        response = pB.dev.connection.ask(f"int:pow {ch},{pB.dev.params[f'channels/{ch}/max-power/set-max-power'].value}").strip("\r")

        if response != "OK":
            pB.dev.log.new_log(f"Setting max power to channel {ch} failed: {response}", "WARNING")
    else:
        pB.dev.log.new_log("Max power out of range. Must be in range [0 dBm, 38 dBm].", "WARNING")

    pB.dev.params[f'channels/{ch}/max-power'].publish_value(float(pB.dev.connection.ask(f"int:pow? {ch}")))


general = {}

general['read-interval'] = {
    'valueInit' : 60.0,
    'settable' : True,
    'broker_func' : read_interval,
    'unit' : 's'
}

general['enable-all'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : enable_all_channels,
}

general['disable-all'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : disable_all_channels,
}

general['reset-all'] = {
    'valueInit' : False,
    'settable' : True,
    'broker_func' : reset_all_interlocks,
}
        
general['fan-speed'] = {
    'valueInit' : 0.0,
    'settable' : True,
    'unit' : '%',
}


initNodes['general'] = general
initNodes['channels'] = {}

for i in range(8):

    # Control
    initNodes['channels'][f'{i}/enable'] = {
        'valueInit' : False,
        'settable' : True,
        'broker_func' : enable_channel,
    }

    initNodes['channels'][f'{i}/reset'] = {
        'valueInit' : False,
        'settable' : True,
        'broker_func' : reset_interlock,
    }

    initNodes['channels'][f'{i}/detected'] = {
        'valueInit' : False,
        'settable' : True,
    }

    initNodes['channels'][f'{i}/status'] = {
        'valueInit' : "",
        'settable' : True,
    }

    initNodes['channels'][f'{i}/current'] = {
        'valueInit' : 0.0,
        'settable' : True,
        'unit' : 'A',
    }

    initNodes['channels'][f'{i}/temperature'] = {
        'valueInit' : 0.0,
        'settable' : True,
        'unit' : '°C',
    }

    initNodes['channels'][f'{i}/input-power'] = {
        'valueInit' : 0.0,
        'settable' : True,
        'unit' : 'dBm',
    }

    initNodes['channels'][f'{i}/output-power'] = {
        'valueInit' : 0.0,
        'settable' : True,
        'unit' : 'dBm',
    }

    initNodes['channels'][f'{i}/reverse-power'] = {
        'valueInit' : 0.0,
        'settable' : True,
        'unit' : 'dBm',
    }

    initNodes['channels'][f'{i}/max-power'] = {
        'valueInit' : 0.0,
        'settable' : True,
        'unit' : 'dBm',
    }

    initNodes['channels'][f'{i}/max-power/set-max-power'] = {
        'valueInit' : 0.0,
        'settable' : True,
        'broker_func' : max_power,
        'unit' : 'dBm',
    }



class DeviceClass(DeviceBase):
    """
    This class is used to communicate with Creotech Booster RF Power Amplifier device over the SCPI interface.
    """

    def init_pre(self, type_address="tcpsocket,10.187.144.91:5000"):
        """
        Constructor of the class.

        Parameters:
        port_name (string): IP address and port

        Returns:
        No returns
        """

        self.initNodes = initNodes
        self.connection_type, self.address = type_address.split(",")

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
            self.connection = scpiPackage.ConnectionClass(devisor=self.devisor, address=f'{self.connection_type},{self.address}')
        except:
            self.dev.log.new_log("Unable to connect to the device.", "ERROR")
            return
        
        # Read initial data
        self.get_control_info()
        self.get_measure_info()
        self.get_interlock_info()

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
            self.dev.log.new_log("Unable to disconnect from the device.", "ERROR")
            return
        
    def get_control_info(self): ### TODO ###
        """
        Function is used to read channel data from Creotech Booster RF Power Amplifier device.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        detected = [True if i=="1" else False for i in "{0:08b}".format(int(self.connection.ask("chan:det? all").strip("\r")))][::-1]
        enabled = [True if i=="1" else False for i in "{0:08b}".format(int(self.connection.ask("chan:enab? all").strip("\r")))][::-1]

        for ch, detected_ch, enabled_ch in zip(range(8), detected, enabled):
            self.params[f'channels/{ch}/detected'].publish_value(detected_ch)
            self.params[f'channels/{ch}/enable'].publish_value(enabled_ch)
        
    def get_measure_info(self): ### TODO ###
        """
        Function is used to read measure data from Creotech Booster RF Power Amplifier device.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        # Measure data
        current = self.connection.ask("meas:curr? all").strip("\r").split(",")
        temperature = self.connection.ask("meas:temp? all").strip("\r").split(",")
        output = self.connection.ask("meas:out? all").strip("\r").split(",")
        input = self.connection.ask("meas:in? all").strip("\r").split(",")
        reverse = self.connection.ask("meas:rev? all").strip("\r").split(",")
        fan_speed = self.connection.ask("meas:fan?").strip("\r")

        # Transfer values to the broker
        for ch, curr_ch, temp_ch, out_ch, in_ch, rev_ch in zip(range(8), current, temperature, output, input, reverse):
            self.params[f'channels/{ch}/current'].publish_value(float(curr_ch))
            self.params[f'channels/{ch}/temperature'].publish_value(float(temp_ch))
            self.params[f'channels/{ch}/input-power'].publish_value(float(in_ch))
            self.params[f'channels/{ch}/output-power'].publish_value(float(out_ch))
            self.params[f'channels/{ch}/reverse-power'].publish_value(float(rev_ch))
        self.params['general/fan-speed'].publish_value(float(fan_speed))

        
    def get_interlock_info(self): ### TODO ###
        """
        Function is used to read interlock data from Creotech Booster RF Power Amplifier device.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        # Interlock power
        for ch in range(8):
            power = self.connection.ask(f"int:pow? {ch}")
            self.params[f'channels/{ch}/max-power'].publish_value(float(power))

        # Interlock status
        status = [True if i=="1" else False for i in "{0:08b}".format(int(self.connection.ask("int:stat? all").strip("\r")))][::-1]
        error = [True if i=="1" else False for i in "{0:08b}".format(int(self.connection.ask("int:err? all").strip("\r")))][::-1]

        for ch, stat_ch, err_ch in zip(range(8), status, error):
            self.params[f'channels/{ch}/status'].publish_value("ERROR" if err_ch else "OVERLOAD" if stat_ch else "OK")

    def read_loop(self):
        """
        Function is used to read parameters and status from Creotech Booster RF Power Amplifier device.

        Parameters:
        No parameters

        Returns:
        No returns
        """

        last_reading = time.time()-float(self.params['general/read-interval'].value)
        while not self.stopThreads and float(self.params['general/read-interval'].value) > 1e-5:

            if time.time()-last_reading > float(self.params['general/read-interval'].value):
                self.get_control_info()
                self.get_measure_info()
                self.get_interlock_info()

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