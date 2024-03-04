import re


def mksrga(dev, message):
    """
    Function is called upon receiving initial message from RGAMKS113. This function is the beginning of
    gaining control and communicating with the device.

    Parameters:
    message (string): received async message

    Returns:
    No returns
    """

    dev.init_communication()
    return

def filament_status(dev, message):
    """
    Function is called upon receiving FilamentStatus message from the RGAMKS113.

    Parameters:
    message (string): received async message

    Returns:
    No returns
    """

    regex = re.match('FilamentStatus\s+(?P<number>[1,2])\s+(?P<state>\S+)', message)
    dev.params['filament/state'].publish_value(regex['state'])
    if regex['state'] == "OFF":
        dev.params['filament/control'].publish_value(False)
    return

def filament_time_remaining(dev, message):
    """
    Function is called upon receiving FilamentTimeRemaining message from the RGAMKS113.

    Parameters:
    message (string): received async message

    Returns:
    No returns
    """

    regex = re.match('FilamentTimeRemaining\s+(?P<time>[0-9]*)', message)
    dev.params['filament/time-remaining'].publish_value(regex['time'])
    return

def starting_scan(dev, message):
    """
    Function is called upon receiving StartingScan message from the RGAMKS113.

    Parameters:
    message (string): received async message

    Returns:
    No returns
    """

    regex = re.match('StartingScan\s+(?P<number>[0-9]*\S).*', message)
    dev.currentMeasurement = regex['number']
    dev.params['scan/current-scan'].publish_value(regex['number'])
    return

def starting_measurement(dev, message):
    """
    Function is called upon receiving StartingMeasurement message from the RGAMKS113.

    Parameters:
    message (string): received async message

    Returns:
    No returns
    """

    regex = re.match('StartingMeasurement\s+(?P<name>\S+)', message)
    dev.currentMeasurement = regex['name']
    dev.params['scan/current-measurement'].publish_value(regex['name'])
    return

def zero_reading(dev, message):
    """
    Function is called upon receiving ZeroReading message from the RGAMKS113.

    Parameters:
    message (string): received async message

    Returns:
    No returns
    """

    regex = re.match('ZeroReading\s+(?P<amu>\S+)\s+(?P<value>\S+)', message)
    dev.params['scan/zero-reading'].publish_value(f'{{"mass": {float(regex["amu"])}", "_value": {float(regex["value"])/100}}}')
    return

def mass_reading(dev, message):
    """
    Function is called upon receiving MassReading message from the RGAMKS113.

    Parameters:
    message (string): received async message

    Returns:
    No returns
    """

    regex = re.match('MassReading\s+(?P<amu>\S+)\s+(?P<value>\S+)', message)
    dev.params['scan/mass-reading'].publish_value(f'{{"mass": {float(regex["amu"])}, "_value": {float(regex["value"])/100}}}')
    dev.measurementsRemaining -= 1

    return



# Dictionary of all async messages
asyncNotification = {
    'MKSRGA' : mksrga,
    'FilamentStatus' : filament_status,
    'FilamentTimeRemaining' : filament_time_remaining,
    'StartingScan' : starting_scan,
    'StartingMeasurement' : starting_measurement,
    'ZeroReading' : zero_reading,
    'MassReading' : mass_reading,
    'MultAutoSkip' : None,
    'MultiplierStatus' : None,
    'RFTripState' : None,
    'InletChange' : None,
    'AnalogInput' : None,
    'TotalPressure' : None,
    'DigitalPortChange' : None,
    'RVCPumpStatus' : None,
    'RVCHeaterStatus' : None,
    'RVCValveStatus' : None,
    'RVCInterlocks' : None,
    'RVCStatus' : None,
    'RVCDigitalInput' : None,
    'LinkDown' : None,
    'VSCEvent' : None,
    'DegasReading' : None,
    'DiagnosticInput' : None
}