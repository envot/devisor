#!/usr/bin/env python
#  -*- coding: utf-8 -*-
#
# Copyright 2020 by kiutra GmbH
# All rights reserved.
# This file is part of Kiutra-Core,
# and is released under the "Apache Version 2.0 License". Please see the LICENSE
# file that should have been included as part of this package.

from jsonrpclib import Server
import time
#from werkzeug.security import generate_password_hash

DEVICE_READY = 000
DEVICE_BUSY = 123
DEVICE_TIMEOUT = 124
DEVICE_NOT_REACHABLE = 125
DEVICE_ACCESS_DENIED = 126


class KiutraClient(object):
    """
    A class that provides an interface to the kiutra RPC server.
    The RPC server usually implements the interface to all hardware
    and guarantees serialization of device communication.
    Use the basic client as follows:

    .. code-block:: python

        from kiutra_api.api_client import KiutraClient
        if __name__=='__main__':
            client = KiutraClient('192.168.XX.XX')
            # Get controller temperature
            client.query('temperature_control.kelvin')
            # Ramp to 50 K with a ramp rate of 0.25 K/min
            client.call('temperature_control.start', (50, 0.25))
            # Start a sequence first stabilizing 0.1 K for 120 s with a ramp rate of
            # 0.15 K/min, subsequently ramping to 5 K with a ramp rate of 0.2 K/min.
            client.call('temperature_control.start_sequence',
                        [(0.1, 0.15, 120), (5.0, 0.2, 0)])



    Alternatively, the pre defined client classes provided in this package are ready to use, offering all necessary interfacing
    options to give you full control of your cryostat.
    """

    def __init__(self, host, port=1006, max_retry=10):
        self.max_retry = max_retry
        self.host = host
        self.port = port


    @property
    def server(self):
        return Server('http://{}:{}'.format(self.host, self.port))

    def call(self, key, *args, **kwargs):
        """
        Calls a remote procedure function based on a key and passes arguments.

        :param key:  function handle like device.function
        :param args: arguments
        """
        if len(args) >= 0 and len(kwargs) == 0:
            return self.procedure_call(self.server.call, key, *args)
        elif len(kwargs) > 0 and len(args) == 0:
            return self.procedure_call(self.server.call, key=key, **kwargs)
        else:
            raise AttributeError('You cannot use both *args and **kwargs at the same time with this RPC server')

    def query(self, key):
        """
        Queries a parameter based on key.

        :param key: parameter handle like device.parameter
        """
        return self.procedure_call(self.server.read, key)

    def set(self, key, value):
        """
        Sets a parameter based on key to value.

        :param key: parameter handle like device.parameter
        :param value: target value
        """
        return self.procedure_call(self.server.write, key, value)

    def procedure_call(self, handle, *args, **kwargs):
        retry = 0
        while retry < self.max_retry:
            try:
                if len(kwargs) > 0:
                    ret = handle(**kwargs)
                else:
                    ret = handle(*args)
                status_code = ret['MessageCode']
                if status_code == DEVICE_READY:
                    return ret['Message']
                elif status_code == DEVICE_NOT_REACHABLE:
                    raise ConnectionError('Device not reachable error')
                elif status_code == DEVICE_ACCESS_DENIED:
                    raise ConnectionError('Command not available')
            except ConnectionError as e:
                raise Exception(e)
            except Exception as e:
                pass
            time.sleep(0.02)
            retry += 1
        raise Exception('Max retry reached')


#class Device(KiutraClient):
#    """
#    Use client device like illustrated below:
#
#    .. code-block:: python
#
#        device = Device('hs1', '192.168.XX.XX')
#        code, message = device.status
#        device.reset()
#
#    """
#
#    def __init__(self, device, host, port=1006, max_retry=10):
#        super(Device, self).__init__(host, port, max_retry)
#        self.device = device
#
#    def handle(self, key):
#        return f'{self.device}.{key}'
#
#    def query_value(self, key):
#        return self.query(self.handle(key))
#
#    def set_value(self, key, value):
#        self.set(self.handle(key), value)
#
#    def call_method(self, key, *args, **kwargs):
#        return self.call(self.handle(key), *args, **kwargs)
#
#    @property
#    def api(self) -> dict:
#        """
#        API documentation computed at runtime based on the device implementation.
#
#        """
#        return self.query_value('api')
#
#    @property
#    def status(self) -> (int, str):
#        """
#        Tuple representing the device status as int and a message.
#
#        """
#        return self.query_value('status')
#
#    def reset(self):
#        """
#        Resets device.
#
#        """
#        return self.call_method('reset')
#
#
#class APIManager(Device):
#    """
#    The API manager devices handles unlocking and locking of protected access levels.
#    It also provides an overview of available api accessible devices.
#    """
#    def __init__(self, host, port=1006, max_retry=10):
#        super(APIManager, self).__init__('api_manager', host, port, max_retry)
#
#    def unlock(self, pw: str, level: str) -> bool:
#        """
#        Unlock protected access level for 5 minutes.
#
#        Args:
#            pw: Passphrase
#            level: level like e.-g. 'admin'
#
#        """
#        print(pw)
#        print(level)
#        return self.call_method('unlock', generate_password_hash(pw), level)
#
#    def lock(self):
#        """
#        Locks API access to base level
#
#        """
#        response = self.call_method('lock')['Message']
#        return response
#
#    @property
#    def access_level(self) -> str:
#        """
#        Access level as string.
#
#        """
#        return self.query_value('access_level')
#
#    def restart_service(self):
#        """
#        Restarts kiutra software. This will stop any ongoing control process und close all valves.
#
#        """
#        return self.call_method('restart_service')
#
#    @property
#    def api_info(self):
#        """
#        List of available api devices
#
#        Returns (list): available api devices as string handles
#
#        """
#        return self.query_value('api_info')
