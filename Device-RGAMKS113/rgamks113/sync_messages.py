import re


def accept_protocol_response(dev, message):
    """
    Function is called upon receiving AcceptProtocol response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('AcceptProtocol\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def info_response(dev, message):
    """
    Function is called upon receiving Info response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('Info\s+(?P<status>OK|ERROR)\s+[.\s\S]*MaxMass\s+(?P<maxmass>[0-9]*\S+)', message)
    dev.maxMass = int(regex['maxmass'])
    return

def control_response(dev, message):
    """
    Function is called upon receiving Control response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('Control\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def release_response(dev, message):
    """
    Function is called upon receiving Release response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('Release\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def filament_control_response(dev, message):
    """
    Function is called upon receiving FilamentControl response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('FilamentControl\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def filament_info_response(dev, message):
    """
    Function is called upon receiving FilamentInfo response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('FilamentInfo\s+(?P<status>OK|ERROR)\s+SummaryState\s+(?P<state>\S+)\s+ActiveFilament\s+(?P<number>[1,2])[.\s\S]+\s+MaxOnTime\s+(?P<maxOnTime>[0-9]*)\s+OnTimeRemaining\s+(?P<onTime>[0-9]*)', message)
    dev.params['filament/state'].publish_value(regex['state'])
    dev.params['filament/select'].publish_value(regex['number'])
    dev.params['filament/time-remaining'].publish_value(regex['onTime'])
    dev.params['filament/time-on'].publish_value(regex['maxOnTime'])

    return True if regex['status'] == 'OK' else False

def filament_select_response(dev, message):
    """
    Function is called upon receiving FilamentSelect response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('FilamentSelect\s+(?P<status>OK|ERROR)\s+(Number\s+(?P<number>[1,2]))', message)
    return True if regex['status'] == 'OK' else False

def filament_on_time_response(dev, message):
    """
    Function is called upon receiving FilamentOnTime response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('FilamentOnTime\s+(?P<status>OK|ERROR)\s+(Time\s+(?P<time>[0-9]*))', message)
    dev.maxFilamentOnTime = regex['time']
    dev.params['filament/time-on'].publish_value(regex['time'])
    return True if regex['status'] == 'OK' else False

def scan_add_response(dev, message):
    """
    Function is called upon receiving ScanAdd response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('ScanAdd\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def scan_start_response(dev, message):
    """
    Function is called upon receiving ScanStart response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('ScanStart\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def scan_stop_response(dev, message):
    """
    Function is called upon receiving ScanStop response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('ScanStop\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def scan_resume_response(dev, message):
    """
    Function is called upon receiving ScanResume response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('ScanResume\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def add_analog_response(dev, message):
    """
    Function is called upon receiving AddAnalog response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('AddAnalog\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def add_barchart_response(dev, message):
    """
    Function is called upon receiving AddBarchart response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('AddBarchart\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def add_peak_jump_response(dev, message):
    """
    Function is called upon receiving AddPeakJump response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('AddPeakJump\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def add_single_peak_response(dev, message):
    """
    Function is called upon receiving AddSinglePeak response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('AddSinglePeak\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def measurement_remove_response(dev, message):
    """
    Function is called upon receiving MeasurementRemove response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('MeasurementRemove\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False

def measurement_remove_all_response(dev, message):
    """
    Function is called upon receiving MeasurementRemoveAll response from the RGAMKS113.

    Parameters:
    message (string): received sync message

    Returns:
    (bool): True if there is no error, else False
    """

    regex = re.match('MeasurementRemoveAll\s+(?P<status>OK|ERROR)', message)
    return True if regex['status'] == 'OK' else False



# Dictionary of all sync messages
syncResponse = {
    'AcceptProtocol' : accept_protocol_response,
    'Info' : info_response,
    'Control' : control_response,
    'Release' : release_response,
    'FilamentControl' : filament_control_response,
    'FilamentInfo' : filament_info_response,
    'FilamentSelect' : filament_select_response,
    'FilamentOnTime' : filament_on_time_response,
    'AddAnalog' : add_analog_response,
    'AddBarchart' : add_barchart_response,
    'AddPeakJump' : add_peak_jump_response,
    'AddSinglePeak' : add_single_peak_response,
    'ScanAdd' : scan_add_response,
    'ScanStart' : scan_start_response,
    'ScanStop' : scan_stop_response,
    'ScanResume' : scan_resume_response,
    'MeasurementRemove' : measurement_remove_response,
    'MeasurementRemoveAll' : measurement_remove_all_response,
}