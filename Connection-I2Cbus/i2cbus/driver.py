#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in an EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

REGISTER_LENGTH = 8
DEVICE_FUNCTION_ARRAY = [[]] * (REGISTER_LENGTH+1)

import smbus

class ConnectionClass():
    def __init__(self, devisor, addresses="1,0x20"):
        self.devisor = devisor
        addressesArray = addresses.split(',')
        self.i2cBusAddress = int(addressesArray[0])
        self.i2cDeviceAddress = int(addressesArray[1], 16)
        self.bus = smbus.SMBus(self.i2cBusAddress)
        self.registers = {}
        self.deviceFunctions= {}
        self.registerNames = {}
        self.init_pre()
        self.init_standards()
        self.init_after()

    def init_pre(self):
        pass

    def init_standards(self):
        for address_name in self.registerNames:
            address = self.registerNames[address_name]
            self.deviceFunctions[address] = DEVICE_FUNCTION_ARRAY.copy()
            self.registers[address] = 0
            self.read_register(address)
        
    def init_after(self):
        pass


    def write(self, address, value):
        self.bus.write_byte_data(self.i2cDeviceAddress, address, value)
        return True

    def read(self, address):
        return self.bus.read_byte_data(self.i2cDeviceAddress, address)


    def write_bit(self, address, bit, bitValue):
        if type(address) == str:
            address = self.registerNames[address]
        curregister_str = self._convert_value(self.registers[address])
        self.write_register(address, self._change_bit_Str(curregister_str, bit, bitValue))
        return True

    def write_registers(self, addresses, values):
        for i,address in enumerate(addresses):
            self.write_register(addresses[i], values[i])

    def write_register(self, address, regValue):
        oldRegister = self._convert_value(self.registers[address])
        if type(address) == str:
            address = self.registerNames[address]
        if type(regValue) == str:
            regValueStr = regValue
            regValue = self._convert_value(regValue)
        else:
            regValueStr = self._convert_value(regValue)
        self.registers[address] = regValue
        self.write(address, regValue)
        return self._trigger_regValueStr(address, oldRegister)


    def read_bit(self, address, bit):
        self.read_register(address)
        bit_value = self._read_bit_Str(self._convert_value(self.registers[address]), bit)
        return bool(bit_value)

    def read_registers(self, addresses):
        changed = []
        for address in addresses:
            changed.append(self.read_register(address))
        return changed

    def read_register(self, address):
        oldRegister = self._convert_value(self.registers[address])
        self.registers[address] = self.read(address)
        return self._trigger_regValueStr(address, oldRegister)


    def _trigger_regValueStr(self, address, oldRegister):
        self._trigger_functions(address, -1, self.registers[address])
        changed = []
        for bit,bitValue in enumerate(oldRegister):
            if bitValue != self._convert_value(self.registers[address])[bit]:
                self._trigger_functions(address, bit, bitValue)
                changed.append(bit)
        return changed

    def _trigger_functions(self, address, pos, value):
        for device_func in self.deviceFunctions[address][pos]:
            device_func(value)

    def _convert_value(self, regValue):
        if type(regValue) == str:
            if len(regValue) == REGISTER_LENGTH:
                return int(regValue[::-1], 2)
            else:
                raise Exception('String Value not convertable to int.')
        if type(regValue) == int:
            return format(regValue, '08b')[::-1]

    def _change_bit_Str(self, bitsStr, bit, bitValue):
        bitsStrList = list(bitsStr)
        bitsStrList[bit] = str(int(bitValue))
        return "".join(bitsStrList)

    def _read_bit_Str(self, bitsStr, bit):
        return int(bitsStr[bit])
