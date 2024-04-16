import time
from threading import Thread
import toptica.lasersdk.dlcpro.v2_6_0 as dlcpro
from toptica.lasersdk.dlcpro.v2_6_0 import Client, NetworkConnection, UserLevel


def find_all_components(package):
    """
    Function gathers all possible parameters from.

    Parameters:
    package : package
    
    Returns:
    No returns
    """

    components = {}
    f = open(package.__file__, 'r')
    lines = f.readlines()
    found = False
    for line in lines:
        if 'class ' in line:
            found = True
            component = line[6:-2]
            components[component] = {}
        if found:
            if "'" in line:
                components[component][line[line.find("'")+1:-3]] = line[
                        line.find('=')+2:line.find("(")]
            if len(line)<3:
                found = False
    return components

def test_param(client, param):
    """
    Function tests if certain parameter is available.

    Parameters:
    client (object): Client object
    param (string): name of the parameter
    
    Returns:
    No returns
    """

    try:
        value = client.get(param)
        return [True, value]
    except:
        return [False, None]

def check_components(client, components, component, componentsWorking, partString=''):
    """
    Function checks if certain parameter is available and gathers all available parameters.

    Parameters:
    client (object): Client object
    components (dict): dictionary of all possible parameters
    component (string): name of the top-most component
    componentsWorking (dict): dictionary of all available/working parameters
    partString (string): name of the part of the component
    
    Returns:
    No returns
    """

    parts = components[component]
    for part in parts:
        partType = parts[part]
        [status, value] = test_param(client, partString+part)
        if partType in components:
            if status:
                check_components(client, components, partType, componentsWorking, partString=partString+part)
        else:
            if status:
                initDict = {
                        'valueInit' : value,
                        }
                if type(value) == float:
                    if 'temp' in part:
                        initDict['unit'] = '°C'
                    if 'hum' in part:
                        initDict['unit'] = '%'
                    if 'press' in part:
                        initDict['unit'] = 'hPa'
                    if 'load' in part:
                        initDict['unit'] = 'W'
                    if 'volt' in part:
                        initDict['unit'] = 'V'
                    if 'curr' in part:
                        if 'power-supply' in partString:
                            initDict['unit'] = 'A'
                        else:
                            initDict['unit'] = 'mA'
                if 'Mutable' in partType:
                    initDict['settable'] = True
                componentsWorking[partString+part] = initDict

def find_working_components(device):
    """
    Function checks if certain parameter is available and gathers all available parameters.

    Parameters:
    device (object): DLC device
    
    Returns:
    componentsWorking (dict): dictionary of working parameters
    """

    # Get all possible components
    components = find_all_components(dlcpro)

    # Open connection
    client = Client(NetworkConnection(device.address))
    client.open()

    try: 
        client.change_ul(device.userlevel["ul"], device.userlevel["password"])
        device.devisor.log.new_log(f"Connected as {device.userlevel['name']} for parameter acquisition.", "INFO")
    except Exception as e:
        client.change_ul(UserLevel.NORMAL, "")
        device.devisor.log.new_log(f"Incorrect password. Connected as \"NORMAL\" for parameter acquisition.", "WARNING")

    # Get all working components
    componentsWorking = {}
    check_components(client, components, 'DLCpro', componentsWorking)
    
    client.close()

    return componentsWorking

def transform(components):
    """
    Function transforms parameter names.

    Parameters:
    components (dict): dictionary of all parameters
    
    Returns:
    new_components (dict): transformet dictionary of all parameters
    """

    new_components = {}
    for name, config in components.items():

        new_components[name.replace(":", ".").replace("-", "_")] = config

    return new_components
        
def build_mqtt_nodes(device):
    """
    Function builds MQTT nodes based on gathered available parameters.

    Parameters:
    device (object): DLC device
    
    Returns:
    initNodes (dict): dictionary of MQTT nodes
    components (dict): transformet dictionary of all parameters 
    """
    
    initNodes = {}
    initNodes["control"] = {}
    initNodes["control"]["reconnect"] = {
        'valueInit' : False,
        'broker_func' : reconnect_handle,
        'datatype' : 'boolean',
        'brokerInit' : False,
        'settable' : True,
    }
    initNodes["control"]["read-interval"] = {
        'valueInit' : 60.0,
        'settable' : True,
        'broker_func' : read_interval_handle,
        'unit' : 's'
    }

    components = transform(find_working_components(device))

    for node, config in components.items():

        new_nodes = node.replace("_", "-").split(".")

        if len(new_nodes) == 1:
            new_nodes = ["system", new_nodes[0]]

        if new_nodes[0] not in initNodes.keys():
            initNodes[new_nodes[0]] = {}
        
        config.update({"broker_func": param_handle})
        initNodes[new_nodes[0]]["/".join(new_nodes[1:])] = config

    return initNodes, components

# MQTT handle functions
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
        pB.dev.disconnect()
    except:
        pass
    try:
        pB.dev.connect()
    except:
        pass

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

def param_handle(pB):
    """
    Function is used to handle parameter node change.

    Parameters:
    pB (dict): parameter base

    Returns:
    No returns
    """

    # Set value
    try:
        current = pB.dev.connection
        for i in pB.param.replace("-", "_").split("/"):
            current = getattr(current, i)
        getattr(current, "set")(pB.dev.params[pB.param].value)
    except Exception as e:
        pB.dev.devisor.log.new_log(f"Failed setting \"{pB.param}\".", "WARNING")

    # Get value
    # try:
    #     current = pB.dev.connection
    #     for i in pB.param.replace("-", "_").split("/"):
    #         current = getattr(current, i)
    #     pB.dev.params[pB.param].publish_value(getattr(current, "get")())
    # except Exception as e:
    #     pB.dev.devisor.log.new_log(f"Failed getting \"{pB.param}\".", "WARNING")
    time.sleep(1)
    pB.dev.connection.poll()