import time
from threading import Thread


initNodes = {}

# Connection node
def connection_handle(pB):
    """
    This function is used connect/disconnect to/from RGAMKS113 device.

    Parameters:
    pB : parameters base

    Returns:
    No returns
    """

    if pB.dev.params['connection/connect'].value:
        pB.dev.connect()
    else:
        pB.dev.disconnect()

connection = {}

connection['connect'] = {
    'valueInit' : False,
    'broker_func' : connection_handle,
    'settable' : True,
    'brokerInit' : False,
}

initNodes['connection'] = connection

# Filament node
def filament_control_thread(pB):
    """
    This function is used to turn the filament ON / OFF. When turning the filament ON, it first
    checks if the pressure is low enough ( < 1e-5 mbar ).

    Parameters:
    pB

    Returns:
    No returns
    """

    if pB.dev.params['filament/control'].value:
        try:
            # Read pressure now
            pB.dev.client.publish("agilentxgs600/vagaco/pressure/read-now/set", payload="true", qos=1, retain=True)
            startTime = time.time()
            pB.dev.readNow = True
            while pB.dev.readNow:
                if time.time()-startTime > pB.dev.readPressureTimeout:
                    pB.dev.log.new_log("Pressure read timeout", 'WARNING')
                    pB.dev.params['filament/control'].publish_value(False)
                    return

            # Check if pressure is low enough
            if pB.dev.totalPressure > 0.0 and pB.dev.totalPressure < 1e-5:
                pB.dev.sync_communication("FilamentControl On\n"),
                return
            else:
                pB.dev.log.new_log("Pressure too high.", 'WARNING')
                time.sleep(0.1)
                pB.dev.params['filament/control'].publish_value(False)
        except:
            pB.dev.log.new_log("Pressure incorrect.", 'WARNING')
            time.sleep(0.1)
            pB.dev.params['filament/control'].publish_value(False)

    elif not pB.dev.params['filament/control'].value:
        pB.dev.sync_communication("FilamentControl Off\n")


def filament_control(pB):
    """
    This function starts new thread in order to turn the filament ON / OFF.

    Parameters:
    pB

    Returns:
    No returns
    """

    pB.dev.filamentController = Thread(target = filament_control_thread, args=(pB,))
    pB.dev.filamentController.start()


filament = {}

filament['pressure-sensor'] = {
    'valueInit' : 'agilentxgs600/vagaco/pressure/img1',
    'brokerInit' : False,
    'settable' : True,
}

filament['select'] = {
    'valueInit' : '1',
    'format' : ['1', '2'],
    'broker_func' : lambda pB: pB.dev.sync_communication(f"FilamentSelect {pB.dev.params['filament/select'].value}\n"),
    'datatype' : 'enum',
    'settable' : True,
}
filament['state'] = {
    'valueInit' : 'OFF',
    'brokerInit' : False,
}
filament['time-on'] = {
    'valueInit' : 0,
    'format' : '60:43200',
    'broker_func' : lambda pB: pB.dev.sync_communication(f"FilamentOnTime {pB.dev.params['filament/time-on'].value}\n"),
    'settable' : True,
    'brokerInit' : False,
    'unit' : 's',
}
filament['time-remaining'] = {
    'valueInit' : 0,
    'brokerInit' : False,
    'unit' : 's',
}
filament['control'] = {
    'valueInit' : False,
    'broker_func' : filament_control,
    'settable' : True,
}

initNodes['filament'] = filament





# Measurement node
def measurement_add_analog(pB):
    """
    This function adds new Analog measurement to the RGAMKS113 but first checks if all parameters are valid.

    Parameters:
    pB

    Returns:
    No returns
    """

    is_ok = True
    if pB.dev.params['scan/start-stop'].value:
        pB.dev.log.new_log(f"Scan is running.", 'WARNING')
        is_ok = False

    if is_ok:
        name = pB.dev.params['measurement/add-analog/name'].value
        startMass = int(pB.dev.params['measurement/add-analog/start-mass'].value)
        endMass = int(pB.dev.params['measurement/add-analog/end-mass'].value)
        pointsPerPeak = int(pB.dev.params['measurement/add-analog/points-per-peak'].value)
        accuracy = pB.dev.params['measurement/add-analog/accuracy'].value
        egain = pB.dev.params['measurement/add-analog/egain'].value
        source = pB.dev.params['measurement/add-analog/source'].value
        detector = pB.dev.params['measurement/add-analog/detector'].value

        # Check values
        if name == "":
            pB.dev.log.new_log(f"Measurement name is empty", 'WARNING')
            is_ok = False
        elif name in pB.dev.params['scan/add/select/$format'].value:
            pB.dev.log.new_log(f"Measurement with name \"{name}\" already exist.", 'WARNING')
            is_ok = False
        if startMass < 1 or startMass > pB.dev.maxMass:
            pB.dev.log.new_log(f"Start mass out of range", 'WARNING')
            is_ok = False
        if endMass < startMass or endMass > pB.dev.maxMass:
            pB.dev.log.new_log(f"End mass out of range", 'WARNING')
            is_ok = False

    # Send message to the sensor
    if is_ok:
        pB.dev.addedMeasurements[name] = {"num-of-measurements": pointsPerPeak*(endMass-startMass+1)}
        pB.dev.sync_communication(f"AddAnalog {name} {startMass} {endMass} {pointsPerPeak} {accuracy} {egain} {source} {detector}\n")

        pB.dev.params['measurement/remove/select/$format'].value.append(pB.dev.params['measurement/add-analog/name'].value)
        pB.dev.params['measurement/remove/select/$format'].publish_value()
        pB.dev.params['scan/add/select/$format'].value.append(pB.dev.params['measurement/add-analog/name'].value)
        pB.dev.params['scan/add/select/$format'].publish_value()

    time.sleep(0.1)
    pB.dev.params['measurement/add-analog'].publish_value(False)

    return

def measurement_add_barchart(pB):
    """
    This function adds new Barchart measurement to the RGAMKS113 but first checks if all parameters are valid.

    Parameters:
    pB

    Returns:
    No returns
    """

    is_ok = True
    if pB.dev.params['scan/start-stop'].value:
        pB.dev.log.new_log(f"Scan is running.", 'WARNING')
        is_ok = False

    if is_ok:
        name = pB.dev.params['measurement/add-barchart/name'].value
        startMass = int(pB.dev.params['measurement/add-barchart/start-mass'].value)
        endMass = int(pB.dev.params['measurement/add-barchart/end-mass'].value)
        filterMode = pB.dev.params['measurement/add-barchart/filter-mode'].value
        accuracy = pB.dev.params['measurement/add-barchart/accuracy'].value
        egain = pB.dev.params['measurement/add-barchart/egain'].value
        source = pB.dev.params['measurement/add-barchart/source'].value
        detector = pB.dev.params['measurement/add-barchart/detector'].value

        # Check values
        if name == "":
            pB.dev.log.new_log(f"Measurement name is empty", 'WARNING')
            is_ok = False
        elif name in pB.dev.params['scan/add/select/$format'].value:
            pB.dev.log.new_log(f"Measurement with name \"{name}\" already exist.", 'WARNING')
            is_ok = False
        if startMass < 1 or startMass > pB.dev.maxMass:
            pB.dev.log.new_log(f"Start mass out of range", 'WARNING')
            is_ok = False
        if endMass < startMass or endMass > pB.dev.maxMass:
            pB.dev.log.new_log(f"End mass out of range", 'WARNING')
            is_ok = False


    # Send message to the sensor
    if is_ok:
        pB.dev.addedMeasurements[name] = {"num-of-measurements": endMass-startMass+1}
        pB.dev.sync_communication(f"AddBarchart {name} {startMass} {endMass} {filterMode} {accuracy} {egain} {source} {detector}\n")

        pB.dev.params['measurement/remove/select/$format'].value.append(pB.dev.params['measurement/add-barchart/name'].value)
        pB.dev.params['measurement/remove/select/$format'].publish_value()
        pB.dev.params['scan/add/select/$format'].value.append(pB.dev.params['measurement/add-barchart/name'].value)
        pB.dev.params['scan/add/select/$format'].publish_value()

    time.sleep(0.1)
    pB.dev.params['measurement/add-barchart'].publish_value(False)

    return

def measurement_add_peak_jump(pB):
    """
    This function adds new PeakJump measurement to the RGAMKS113 but first checks if all parameters are valid.

    Parameters:
    pB

    Returns:
    No returns
    """

    is_ok = True
    if pB.dev.params['scan/start-stop'].value:
        pB.dev.log.new_log(f"Scan is running.", 'WARNING')
        is_ok = False

    if is_ok:
        name = pB.dev.params['measurement/add-peak-jump/name'].value
        filterMode = pB.dev.params['measurement/add-peak-jump/filter-mode'].value
        accuracy = pB.dev.params['measurement/add-peak-jump/accuracy'].value
        egain = pB.dev.params['measurement/add-peak-jump/egain'].value
        source = pB.dev.params['measurement/add-peak-jump/source'].value
        detector = pB.dev.params['measurement/add-peak-jump/detector'].value

        # Check values
        if name == "":
            pB.dev.log.new_log(f"Measurement name is empty", 'WARNING')
            is_ok = False
        elif name in pB.dev.params['scan/add/select/$format'].value:
            pB.dev.log.new_log(f"Measurement with name \"{name}\" already exist.", 'WARNING')
            is_ok = False

    # Send message to the sensor
    if is_ok:
        pB.dev.addedMeasurements[name] = {"num-of-measurements": 1}
        pB.dev.sync_communication(f"AddPeakJump {name} {filterMode} {accuracy} {egain} {source} {detector}\n")

        pB.dev.params['measurement/remove/select/$format'].value.append(pB.dev.params['measurement/add-peak-jump/name'].value)
        pB.dev.params['measurement/remove/select/$format'].publish_value()
        pB.dev.params['scan/add/select/$format'].value.append(pB.dev.params['measurement/add-peak-jump/name'].value)
        pB.dev.params['scan/add/select/$format'].publish_value()

    time.sleep(0.1)
    pB.dev.params['measurement/add-peak-jump'].publish_value(False)

    return

def measurement_add_single_peak(pB):
    """
    This function adds new SinglePeak measurement to the RGAMKS113 but first checks if all parameters are valid.

    Parameters:
    pB

    Returns:
    No returns
    """

    is_ok = True
    if pB.dev.params['scan/start-stop'].value:
        pB.dev.log.new_log(f"Scan is running.", 'WARNING')
        is_ok = False

    if is_ok:
        name = pB.dev.params['measurement/add-single-peak/name'].value
        mass = float(pB.dev.params['measurement/add-single-peak/mass'].value)
        accuracy = pB.dev.params['measurement/add-single-peak/accuracy'].value
        egain = pB.dev.params['measurement/add-single-peak/egain'].value
        source = pB.dev.params['measurement/add-single-peak/source'].value
        detector = pB.dev.params['measurement/add-single-peak/detector'].value

        # Check values
        if name == "":
            pB.dev.log.new_log(f"Measurement name is empty", 'WARNING')
            is_ok = False
        elif name in pB.dev.params['scan/add/select/$format'].value:
            pB.dev.log.new_log(f"Measurement with name \"{name}\" already exist.", 'WARNING')
            is_ok = False
        if mass < 1 or mass > pB.dev.maxMass:
            pB.dev.log.new_log(f"Mass out of range", 'WARNING')
            is_ok = False

    # Send message to the sensor
    if is_ok:
        pB.dev.addedMeasurements[name] = {"num-of-measurements": 1}
        pB.dev.sync_communication(f"AddSinglePeak {name} {mass} {accuracy} {egain} {source} {detector}\n")

        pB.dev.params['measurement/remove/select/$format'].value.append(pB.dev.params['measurement/add-single-peak/name'].value)
        pB.dev.params['measurement/remove/select/$format'].publish_value()
        pB.dev.params['scan/add/select/$format'].value.append(pB.dev.params['measurement/add-single-peak/name'].value)
        pB.dev.params['scan/add/select/$format'].publish_value()

    time.sleep(0.1)
    pB.dev.params['measurement/add-single-peak'].publish_value(False)

    return

def measurement_remove(pB):
    """
    This function removes a measurement from RGAMKS113 by name.

    Parameters:
    pB

    Returns:
    No returns
    """

    select = pB.dev.params['measurement/remove/select'].value
    is_ok = True
    if pB.dev.dev.params['scan/repeat'].value:
        pB.dev.log.new_log("Scan repeat is on.", 'WARNING')
        is_ok = False
    if pB.dev.params['scan/start-stop'].value:
        pB.dev.log.new_log("Scan is running.", 'WARNING')
        is_ok = False
    if is_ok and select == "":
        pB.dev.log.new_log("Select a measurement to remove.", 'WARNING')
        is_ok = False

    if is_ok:
        pB.dev.sync_communication(f"MeasurementRemove {select}\n")

        pB.dev.params['measurement/remove/select/$format'].value.remove(select)
        pB.dev.params['measurement/remove/select/$format'].publish_value()
        pB.dev.params['scan/add/select/$format'].value.remove(select)
        pB.dev.params['scan/add/select/$format'].publish_value()

        if pB.dev.params['scan/add/select/$format'].value == []:
            pB.dev.params['measurement/remove/select'].publish_value('')
            pB.dev.params['scan/add/select'].publish_value('')

        temp = pB.dev.params['scan/list'].value.split(', ')
        if select in temp:
            temp.remove(select)
            del pB.dev.addedMeasurements[select]
            pB.dev.params['scan/list'].publish_value(", ".join(temp))

    time.sleep(0.1)
    pB.dev.params['measurement/remove'].publish_value(False)
    return

def measurement_remove_all(pB):
    """
    This function removes all measurements from RGAMKS113

    Parameters:
    pB

    Returns:
    No returns
    """

    is_ok = True
    if pB.dev.dev.params['scan/repeat'].value:
        pB.dev.log.new_log("Scan repeat is on.", 'WARNING')
        is_ok = False

    if pB.dev.params['scan/start-stop'].value:
        pB.dev.log.new_log("Scan is running.", 'WARNING')
        is_ok = False

    if is_ok:
        pB.dev.sync_communication(f"MeasurementRemoveAll\n")

        pB.dev.params['measurement/remove/select'].publish_value('')
        pB.dev.params['measurement/remove/select/$format'].publish_value([])
        pB.dev.params['scan/add/select'].publish_value('')
        pB.dev.params['scan/add/select/$format'].publish_value([])
        pB.dev.params['scan/list'].publish_value('')
        pB.dev.addedMeasurements = dict()

    time.sleep(0.1)
    pB.dev.params['measurement/remove-all'].publish_value(False)
    return


measurement = {}

measurement['add-analog'] = {
    'valueInit' : False,
    'broker_func' : measurement_add_analog,
    'settable' : True,
    'brokerInit' : False,
}
measurement['add-analog/name'] = {
    'valueInit' : '',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-analog/start-mass'] = {
    'valueInit' : 1,
    'settable' : True,
    'unit' : 'amu',
    'brokerInit' : True,
}
measurement['add-analog/end-mass'] = {
    'valueInit' : 1,
    'settable' : True,
    'unit' : 'amu',
    'brokerInit' : True,
}
measurement['add-analog/points-per-peak'] = {
    'valueInit' : '32',
    'format' : ['32', '16', '8', '4'],
    'datatype' : 'enum',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-analog/accuracy'] = {
    'valueInit' : '4',
    'format' : ['0', '1', '2', '3', '4', '5', '6', '7', '8'],
    'datatype' : 'enum',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-analog/egain'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-analog/source'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-analog/detector'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}

measurement['add-barchart'] = {
    'valueInit' : False,
    'broker_func' : measurement_add_barchart,
    'settable' : True,
    'brokerInit' : False,
}
measurement['add-barchart/name'] = {
    'valueInit' : '',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-barchart/start-mass'] = {
    'valueInit' : 1,
    'settable' : True,
    'unit' : 'amu',
    'brokerInit' : True,
}
measurement['add-barchart/end-mass'] = {
    'valueInit' : 1,
    'settable' : True,
    'unit' : 'amu',
    'brokerInit' : True,
}
measurement['add-barchart/filter-mode'] = {
    'valueInit' : 'PeakCenter',
    'format' : ['PeakCenter', 'PeakMax', 'PeakAverage'],
    'datatype' : 'enum',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-barchart/accuracy'] = {
    'valueInit' : '4',
    'format' : ['0', '1', '2', '3', '4', '5', '6', '7', '8'],
    'datatype' : 'enum',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-barchart/egain'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-barchart/source'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-barchart/detector'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}

measurement['add-peak-jump'] = {
    'valueInit' : False,
    'broker_func' : measurement_add_peak_jump,
    'settable' : True,
    'brokerInit' : False,
}
measurement['add-peak-jump/name'] = {
    'valueInit' : '',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-peak-jump/filter-mode'] = {
    'valueInit' : 'PeakCenter',
    'format' : ['PeakCenter', 'PeakMax', 'PeakAverage'],
    'datatype' : 'enum',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-peak-jump/accuracy'] = {
    'valueInit' : '4',
    'format' : ['0', '1', '2', '3', '4', '5', '6', '7', '8'],
    'datatype' : 'enum',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-peak-jump/egain'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-peak-jump/source'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-peak-jump/detector'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}

measurement['add-single-peak'] = {
    'valueInit' : False,
    'broker_func' : measurement_add_single_peak,
    'settable' : True,
    'brokerInit' : False,
}
measurement['add-single-peak/name'] = {
    'valueInit' : '',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-single-peak/mass'] = {
    'valueInit' : 1,
    'settable' : True,
    'unit' : 'amu',
    'brokerInit' : True,
}
measurement['add-single-peak/accuracy'] = {
    'valueInit' : '4',
    'format' : ['0', '1', '2', '3', '4', '5', '6', '7', '8'],
    'datatype' : 'enum',
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-single-peak/egain'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-single-peak/source'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}
measurement['add-single-peak/detector'] = {
    'valueInit' : 0,
    'settable' : True,
    'brokerInit' : True,
}

measurement['remove'] = {
    'valueInit' : False,
    'broker_func' : measurement_remove,
    'settable' : True,
    'brokerInit' : False,
}
measurement['remove/select'] = {
    'valueInit' : '',
    'format' : [],
    'datatype' : 'enum',
    'settable' : True,
    'brokerInit' : False,
}
measurement['remove-all'] = {
    'valueInit' : False,
    'broker_func' : measurement_remove_all,
    'settable' : True,
    'brokerInit' : False,
}

initNodes['measurement'] = measurement





# Scan node
def scan_start_stop(pB):
    """
    This function STARTS / STOPS the scan. Scan can start only if the scan list is not empty.

    Parameters:
    pB

    Returns:
    No returns
    """

    if pB.dev.params['filament/state'].value != "ON":
        pB.dev.log.new_log(f"Filament state is {pB.dev.params['filament/state'].value}, should be ON", 'WARNING')
        pB.dev.params['scan/start-stop'].publish_value(False)
        return

    if pB.dev.params['scan/start-stop'].value:
        is_ok = True
        if pB.dev.params['scan/list'].value == "":
            pB.dev.log.new_log(f"Scan list is empty", 'WARNING')
            pB.dev.params['scan/start-stop'].publish_value(False)
            is_ok = False

        if is_ok:
            pB.dev.scanRepeater = Thread(target = pB.dev.repeat_scan)
            pB.dev.scanRepeater.start()


    elif not pB.dev.params['scan/start-stop'].value:
        pB.dev.sync_communication("ScanStop\n")

        pB.dev.measurementsRemaining = 0
        pB.dev.params['scan/start-stop'].publish_value(False)
        pB.dev.params['scan/repeat'].publish_value(False)
        pB.dev.params['scan/list'].publish_value("")
        pB.dev.params['scan/current-scan'].publish_value("")
        pB.dev.params['scan/current-measurement'].publish_value("")

    return

def scan_add(pB):
    """
    This function adds a measurement (by name) to the scan. Measurement can not be added
    while scan is running.

    Parameters:
    pB

    Returns:
    No returns
    """

    if pB.dev.dev.params['scan/repeat'].value:
        pB.dev.log.new_log("Scan repeat is on.", 'WARNING')
        pB.dev.params['scan/add'].publish_value(False)
        return

    if pB.dev.params['scan/start-stop'].value:
        pB.dev.log.new_log("Scan is running.", 'WARNING')
        pB.dev.params['scan/add'].publish_value(False)
        return

    is_ok = True
    if pB.dev.params['scan/add/select'].value == "":
        pB.dev.log.new_log("Select a measurement to add.", 'WARNING')
        is_ok = False
    elif pB.dev.params['scan/add/select'].value in pB.dev.params['scan/list'].value.split(','):
        pB.dev.log.new_log(f"Measurement with name \"{pB.dev.params['scan/add/select'].value}\" already exist.", 'WARNING')
        is_ok = False
    elif pB.dev.params['scan/add/select'].value not in pB.dev.params['scan/add/select/$format'].value:
        pB.dev.log.new_log(f"Measurement with name \"{pB.dev.params['scan/add/select'].value}\" does not exist.", 'WARNING')
        is_ok = False

    if is_ok:
        pB.dev.params['scan/list'].value += f"{',' if pB.dev.params['scan/list'].value !='' else ''}{pB.dev.params['scan/add/select'].value}"
        pB.dev.params['scan/list'].publish_value()

    pB.dev.sync_communication(f"ScanAdd {pB.dev.params['scan/add/select'].value}\n")

    time.sleep(0.1)
    pB.dev.params['scan/add'].publish_value(False)
    return

def scan_clear(pB):
    """
    This function clears all measurements from the scan.

    Parameters:
    pB

    Returns:
    No returns
    """

    if pB.dev.params['scan/start-stop'].value:
        pB.dev.log.new_log("Scan is running.", 'WARNING')
    elif not pB.dev.params['scan/start-stop'].value:
        pB.dev.sync_communication("ScanStop\n")
        pB.dev.params['scan/list'].publish_value('')
        pB.dev.params['scan/current-scan'].publish_value('')
        pB.dev.params['scan/current-measurement'].publish_value('')

    time.sleep(0.1)
    pB.dev.params['scan/list/clear'].publish_value(False)
    return

scan = {}

scan['add/select'] = {
    'valueInit' : '',
    'format' : [],
    'settable' : True,
    'datatype' : 'enum',
    'brokerInit' : False,
}
scan['add'] = {
    'valueInit' : False,
    'broker_func' : scan_add,
    'settable' : True,
    'brokerInit' : False,
}
scan['list'] = {
    'valueInit' : '',
    'brokerInit' : False,
}
scan['list/clear'] = {
    'valueInit' : False,
    'broker_func' : scan_clear,
    'settable' : True,
    'brokerInit' : False,
}
scan['repeat'] = {
    'valueInit' : False,
    'settable' : True,
    'brokerInit' : False,
}
scan['interval'] = {
    'valueInit' : 1800,
    'settable' : True,
    'unit' : 's',
    'brokerInit' : True,
}
scan['num-of-scans'] = {
    'valueInit' : 1,
    'settable' : True,
    'brokerInit' : True,
}
scan['start-stop'] = {
    'valueInit' : False,
    'broker_func' : scan_start_stop,
    'settable' : True,
    'brokerInit' : False,
}
scan['current-scan'] = {
    'valueInit' : '',
    'settable' : False,
    'brokerInit' : False,
}
scan['current-measurement'] = {
    'valueInit' : '',
    'settable' : False,
    'brokerInit' : False,
}
scan['zero-reading'] = {
    'valueInit' : '',
    'settable' : False,
    'unit' : 'mbar',
    'brokerInit' : False,
}
scan['mass-reading'] = {
    'valueInit' : '',
    'settable' : False,
    'unit' : 'mbar',
    'brokerInit' : False,
}

initNodes['scan'] = scan
