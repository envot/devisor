#!/usr/bin/env python3
# -*- coding: utf-8 -*- 

# Python program to control, monitor and configure devices in a EoT: https://envot.io
# Klemens Schueppert : schueppi@envot.io

from devisor.devisorbase import DeviceBase
import time
import serial

initNodes = {}

def create_servo(pB):
    servoName = pB.dev.params['config/name'].value
    address = pB.dev.params['config/address'].value
    if pB.value:
        if not servoName in pB.dev.params['config/servos'].value:
            pB.dev.create_servo(servoName, address)
        else:
            pB.dev.log.new_log('Servo "'+ servoName + '" already running.')
    pB.publish_value(False)

def handle_servos(pB):
    servos2del = []
    for startedServoName in pB.dev.servos:
        if not startedServoName in pB.value:
            servos2del.append(startedServoName)
    for servo2del in servos2del:
        pB.dev.log.new_log('We close '+servo2del+'.')
        pB.dev.servos[servo2del].exit()
        del(pB.dev.servos[servo2del])
    for servoName in pB.value:
        if not servoName in pB.dev.servos:
            pB.dev.create_servo(servoName, pB.value[servoName])

config = {
    'create': {
        'valueInit' : False,
        'brokerInit' : False,
        'broker_func' : create_servo,
        'settable' : True,
        },
    'name': {
        'valueInit' : 'servo-name',
        'brokerInit' : True,
        'settable' : True,
        },
    'address': {
        'valueInit' : '0',
        'brokerInit' : True,
        'settable' : True,
        },
    'servos': {
        'valueInit' : {},
        'brokerInit' : True,
        'broker_func' : handle_servos,
        'settable' : True,
        },
}

order = list(config.keys())
order.remove('servos')
order.insert(0, 'servos')
initNodes['config'] = config

def broker_change_active(pB):
    if pB.value:
        pB.dev.servo_switch(pB.dev.servos[pB.param.split('/')[1]].id, '01')
    else:
        pB.dev.servo_switch(pB.dev.servos[pB.param.split('/')[1]].id, '00')

servoActiveInitDict = {
    'valueInit' : False,
    'brokerInit' : False, # accessing servo's id not possible at startup
    'broker_func' : broker_change_active,
    'settable' : True,
}

def broker_change_position(pB):
    pps = 40000
    pB.dev.move_abs(pB.value*1e+4, pps, pB.dev.servos[pB.param.split('/')[1]].id)


servoPosInitDict = {
    'valueInit' : 0.,
    'brokerInit' : False, # accessing servo's id not possible at startup
    'format' : "-10:10",
    'broker_func' : broker_change_position,
    'settable' : True,
    'unit' : 'mm',
}

def broker_change_origin(pB):
    if pB.value:
        pB.dev.move_origin(pB.dev.servos[pB.param.split('/')[1]].id)
    else:
        pB.dev.move_origin(pB.dev.servos[pB.param.split('/')[1]].id)

servoOriginInitDict = {
    'valueInit' : False,
    'brokerInit' : False, # accessing servo's id not possible at startup
    'broker_func' : broker_change_origin,
    'settable' : True,
}

class GMTServo():
    def __init__(self, dev, name, address=0):
        self.dev = dev
        self.id = self.dev.convert_id(address)
        self.devisor = dev.devisor
        self.name = name
        self.init_params()

    def init_params(self):
        self.dev.create_property(self.name+'/active', 'servos', servoActiveInitDict)
        self.dev.create_property(self.name+'/position', 'servos', servoPosInitDict)
        self.dev.create_property(self.name+'/move_origin', 'servos', servoOriginInitDict)

    def exit(self):
        self.dev.remove_property(self.name, 'servos')

class DeviceClass(DeviceBase):
    def init_pre(self):
        self.instr = self.devisor.runningConnections.open(self.address)
        self.servos = {}
        self.initNodes = initNodes

    def init_after(self):
        for sname in self.servos:
            servo = self.servos[sname]
            self.params['servos/'+sname+'/position'].publish_value(self.get_actual_pos(servo.id)*1e-4)
            self.params['servos/'+sname+'/active'].publish_value(self.get_axis_status(servo.id))

    def create_servo(self, name, address):
        if name in self.servos:
            self.dev.log.new_log('Servo name "'
                    +name
                    +'" already in running.', 30)
        else:
            self.servos[name] = GMTServo(self, name, self.convert_id(address))
            if 'config/servos' in self.params:
                self.params['config/servos'].value[name] = address
                self.params['config/servos'].publish_value()

    def __close__(self):
        self.instr.close()

    def convert_id(self, servoID):
        return ('%02d' %int(servoID))

    def int_to_twos_complement(self, num, bits):
        """
        builds the twos complement in order to form negative numbers
        """
        if num >= 0:
            return bin(num)[2:].zfill(bits)
        return bin((1 << bits) + num)[2:]   #build twos complement for negative numbers

    def byte_stuffing(self, data):
        """
        Insert AAAA for each AA byte in the frame data
        """
        num_bytes = int(len(data)/2)
        stuffed_data_list = []
        for n in range(num_bytes):
            actual_byte = data[2*n:2*n+2]
            #if byte 0xAA is part of the frame data, it needs to be replaced
            #by 0xAAAA because AA not followed by AA, CC or EE gives an error
            if actual_byte == 'AA':
                stuffed_data_list.append('AAAA')
            else:
                stuffed_data_list.append(actual_byte)
        stuffed_data = ''.join(stuffed_data_list)
        return stuffed_data

    def crc16_ibm(self, dataframe):
        #Calculates 2 Bytes corresponding to the crc16-IBM algorithm
        crc = 0xFFFF                                    #init crc
        len_data = int(len(dataframe)/2)
        for i in range(len_data):
            byte = bytes.fromhex(dataframe[2*i:2*i+2])   #compute byte by byte
            byte = int.from_bytes(byte, byteorder='big') #^operation (xor) only for integers
            crc = crc ^ byte
            for _ in range(8):
                if crc & 0x0001:
                    crc = (crc >> 1) ^ 0xA001           #xor with polynomial 0xA001
                else:
                    crc >>= 1
        crc_str = format(crc, '04x')    #we need 4hex numbers / 2bytes
        crc_str.upper()                  #convert to hex string
        #print(crc_str)
        crc_str_out = crc_str[2:] + crc_str[:2]    #swap bytes and cut away 0x
        #print(crc_str_out)
        return crc_str_out

    def combine_command(self, frame_data,header='AACC', tail='AAEE'):
        #sets together the transmitted command
        frame_data = self.byte_stuffing(frame_data)
        crc_hex = self.crc16_ibm(frame_data)
        hex_data_to_send = header + frame_data + crc_hex + tail
        #print(hex_data_to_send)
        bytes_to_send = bytes.fromhex(hex_data_to_send)
        return bytes_to_send

    def convert_byte_order(self,received_data):
        #in the received data, alway the lowest byte comes first and this needs
        #to be changed in order to be able to compare values for example
        #with the parameter list or to convert easily to decimal numbers
        len_data = int(len(received_data)/2)
        received_data_flipped = ""
        for n in range(len_data,0,-1):
            received_data_flipped =  received_data_flipped + received_data[2*n-2:2*n]
        return received_data_flipped    

    def find_status_string(self,receive_list, frame_data):
        str_receive = ''
        for idx,x in enumerate(receive_list):
            if x[4:8] == frame_data:
                str_receive = receive_list[idx]
                break
        #communication_status = x[8:10]  #still need to store this somewhere
        return str_receive

    def decimal_to_little_endian_hex(self, decimal, num_bytes = 4):
        #Convert decimal numbers to little endian hex because this
        #is the format that the command needs
        format_string = format(2*num_bytes,'02') + 'x'
        if decimal >= 0:
            hex_string = format(decimal, format_string)
            # Assuming 8 characters for 4 bytes in little-endian
        else:
            bin_twos_complement = int(self.int_to_twos_complement(decimal, 8*num_bytes),2)
            hex_string = hex(bin_twos_complement)
            hex_string = hex_string[2:]  # Output: '0x48d'

        little_endian_hex = [hex_string[i:i+2] for i in range(0, len(hex_string), 2)]
        little_endian_hex.reverse()  # Reversing to get little-endian representation
        hex_string_out = ''.join(little_endian_hex) #set list together to string
        hex_string_out = hex_string_out.upper()
        return hex_string_out


    def write_to_bus(self, frame_data):
        bytes_to_send = self.combine_command(frame_data)
        self.instr.write(bytes_to_send, codec=False)

    def read_from_bus(self):
        incoming_bytes = self.instr.read(1000, codec=False)
        received_hex_data = incoming_bytes.hex().upper()
        receive_list = list(received_hex_data.split('AAEE'))
        return receive_list

    def ask_bus(self, frame_data):
        self.write_to_bus(frame_data)
        receive_list = self.read_from_bus()
        return self.find_status_string(receive_list, frame_data)


    def move_abs(self, end_pos, pps, slave_ID):
        #moves stage to the absolute position end_pos
        frame_type = '34'
        pps_hex = self.decimal_to_little_endian_hex(pps)
        end_pos_hex = self.decimal_to_little_endian_hex(int(end_pos))
        frame_data = slave_ID + frame_type + end_pos_hex + pps_hex
        self.write_to_bus(frame_data)

    def servo_switch(self, state, slave_ID):
        #servo off... state='00'
        #servo on...  state='01'
        frame_type = '2A'
        frame_data = slave_ID + frame_type
        self.write_to_bus(frame_data)

    def get_actual_pos(self, slave_ID):
        #read out the actual position of the stage
        frame_type = '53'
        frame_data = slave_ID + frame_type
        str_receive = self.ask_bus(frame_data)
        pos_receive_hex = self.convert_byte_order(str_receive[10:18])
        try:
            pos = int(pos_receive_hex,16)   #convert hex to integer
        except:
            return None

        #In the case of negative numbers position is far out of limit:
        if pos > 2000000000:
            pos = -int(self.int_to_twos_complement(-pos,32),2)
            #convert negative number back via two's complement'
        return pos

    def set_command_position(self, end_pos, slave_ID):
        #sets your actual position to a certain value (without moving)
        #can be used to shift coordinates
        frame_type = '50'
        end_pos_hex = self.decimal_to_little_endian_hex(int(end_pos))
        frame_data = slave_ID + frame_type + end_pos_hex
        self.write_to_bus(frame_data)

    def set_actual_position_as_origin(self, slave_ID):
        #This function sets the position zero to your actual position
        pos = 0
        self.set_command_position(pos,slave_ID)

    def set_actual_position(self, end_pos, slave_ID):
        #sets your actual position to a certain value (without moving)
        #can be used to shift coordinates
        frame_type = '52'
        end_pos_hex = self.decimal_to_little_endian_hex(int(end_pos))
        frame_data = slave_ID + frame_type + end_pos_hex
        self.write_to_bus(frame_data)

    def get_axis_status(self, slave_ID):
        frame_type = '40'
        frame_data = slave_ID + frame_type
        str_receive = self.ask_bus(frame_data)
        status_flag = self.convert_byte_order(str_receive[10:18])
        return status_flag

    def get_pos_error(self, slave_ID):
        #returns difference between command position and actual position
        frame_type = '54'
        frame_data = slave_ID + frame_type
        str_receive = self.ask_bus(frame_data)
        pos_diff_receive_hex = self.convert_byte_order(str_receive[10:18])
        pos_diff = int(pos_diff_receive_hex,16)   #convert hex to integer

        #In the case of negative numbers position is far out of limit:
        if pos_diff > 2000000000:
            pos_diff = -int(self.int_to_twos_complement(-pos_diff,32),2)
            #convert negative number back via two's complement'
        return pos_diff

    def set_parameter(self, param_no, param_val, slave_ID):
        #you need to take care to use the parameter table for the
        #EZI motion plus-R (enumeration of parameters is different for the
        #EZI series without the plus)
        frame_type = '12'
        param_no_hex = self.decimal_to_little_endian_hex(param_no,1)
        param_val_hex = self.decimal_to_little_endian_hex(param_val)
        frame_data = slave_ID + frame_type + param_no_hex + param_val_hex
        self.write_to_bus(frame_data)

    def get_parameter(self, param_no, slave_ID):
        #you need to take care to use the parameter table for the
        #EZI motion plus-R (enumeration of parameters is different for the
        #EZI series without the plus)
        frame_type = '13'
        param_no_hex = self.decimal_to_little_endian_hex(param_no,1)
        frame_data = slave_ID + frame_type + param_no_hex
        #self.write_to_bus(frame_data)
        str_receive = self.ask_bus(frame_data)
        return str_receive

    def move_to_limit(self, direction, pps, slave_ID):
        #direction=0...negative limit
        #direction=1...positive limit
        frame_type = '36'
        pps_hex = self.decimal_to_little_endian_hex(pps)
        direction_hex = self.decimal_to_little_endian_hex(direction,1)
        frame_data = slave_ID + frame_type + pps_hex + direction_hex
        self.write_to_bus(frame_data)

#    TBC
#    cmds = {
#            # name: [frame_type, setable, readable, slave_ID]
#            'save_all_parameters': ['10', True, False],
#            'get_alarm_type': ['2E', False, True, slave_ID],
#            'move_origin_all': ['3D', True, False, '99'],
#            'move_origin': ['33', True, False, slave_ID],
#            'emergency_stop_all': ['3C', True, False, '99'],
#            'emergency_stop': ['32', True, False, slave_ID],
#            }

    def emergency_stop(self, slave_ID):
        #make an emergency stop for the motor with the given slave ID
        frame_type = '32'
        frame_data = slave_ID + frame_type
        self.write_to_bus(frame_data)

    def emergency_stop_all(self):
        #make an emergency stop for all motors on the port
        frame_type = '3C'
        slave_ID = '99'
        frame_data = slave_ID + frame_type
        self.write_to_bus(frame_data)

    def move_origin(self, slave_ID):
        #move single axis to origin depending on the specified origin method which is
        #specified in the parameter no. 20 (this can be set via set_parameter(...))
        frame_type = '33'
        frame_data = slave_ID + frame_type
        self.write_to_bus(frame_data)

    def move_origin_all(self):
        #move all axis to origin depending on the specified origin method which is
        #specified in the parameter no. 20 (this can be set via set_parameter(...))
        frame_type = '3D'
        slave_ID = '99'
        frame_data = slave_ID + frame_type
        self.write_to_bus(frame_data)

    def get_alarm_type(self,slave_ID):
        ''' Alarm type: No alarm (0) OverCurrent(1) OverSpeed(2)
        StepOut(3) OverLoad(4) OverTemperature(5)
        BackEMF(6) MotorConnect(7) EncoderConnect(8)
        MotorPower(9) Inposition(10) SystemHalt(11)
        ROMdevice(12) Position Overflow(15)'''
        frame_type = '2E'
        frame_data = slave_ID + frame_type
        str_receive = self.ask_bus(frame_data)
        alarm_type = str_receive[10:12]
        return alarm_type

    def save_all_parameters(self,slave_ID):
        #saves all the actual parameters to the ROM
        frame_type = '10'
        frame_data = slave_ID + frame_type
        self.write_to_bus(frame_data)

    def save_shift_to_origin(self,slave_ID):
        origin_shift = self.get_actual_pos(slave_ID)
        #store position somewhere on the server because when the servo
        #turns off it forgets about its zero position
        #it needs to be restored after restart via set_actual_position
        #maybe just include a function which reads all the positions
        #of the servos all the time and then use that positions when restarting
