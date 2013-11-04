#===============================================================================
# Copyright (c) 2013, Leo Hendrawan
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the Leo Hendrawan nor the
#    names of its contributors may be used to endorse or promote products
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY LEO HENDRAWAN ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#===============================================================================

#===============================================================================
# Name:        OpenBSLHost.py
#
# Description: Host python script for OpenBSL slave with UART interface
#
# Author:      Leo Hendrawan
#
# Version:     0.3
#
# Licence:     BSD license
#
# Note:        This module requires pyserial (http://pyserial.sourceforge.net/)
#
# Log:
#     - Version 0.3 (2013.02.22) :
#       Hello World! (created)
#
#===============================================================================
#!/usr/bin/env python

import sys
import optparse
import time
import serial
from TiTxtParser import TiTxtParser


#===============================================================================
# Constants
#===============================================================================

# mem info command
OPEN_BSL_GET_MEM_INFO = 0x00

# image related command(s)
OPEN_BSL_CMD_ERASE_IMAGE = 0x01
OPEN_BSL_CMD_DOWNLOAD_IMAGE = 0x02
OPEN_BSL_CMD_UPLOAD_IMAGE = 0x03
OPEN_BSL_CMD_RUN_APP = 0x04

# segment related command(s)
OPEN_BSL_CMD_CALCULATE_CHECKSUM = 0x05
OPEN_BSL_CMD_ERASE_SEGMENT = 0x06
OPEN_BSL_CMD_DOWNLOAD_SEGMENT = 0x07
OPEN_BSL_CMD_UPLOAD_SEGMENT = 0x08

# security related command(s)
OPEN_BSL_CMD_PASSWD = 0x09

# jump address command
OPEN_BSL_CMD_JUMP_ADDR = 0x0A

# sync command
OPEN_BSL_CMD_SYNC = 0x90


# response
OPEN_BSL_RESP_OK = 0x00
OPEN_BSL_RESP_ERR_UNKNOWN_CMD = 0xE1
OPEN_BSL_RESP_ERR_UNSUPPORTED_CMD = 0xE2
OPEN_BSL_RESP_ERR_PASSWORD_PROTECTED = 0xE3
OPEN_BSL_RESP_ERR_INVALID_PARAM = 0xE4
OPEN_BSL_RESP_ERR_INVALID_FORMAT = 0xE5
OPEN_BSL_RESP_ERR_INVALID_CHECKSUM = 0xE6


# positive response bit mask
OPEN_BSL_RESP_BIT_MASK  = 0x80

# command length
OPEN_BSL_CHKSUM_LEN = 2
OPEN_BSL_CMD_PASSWD_LEN = 10

# maximum sync retry
MAX_SYNC_RETRY  = 100

# mem info dict keys
MEM_INFO_NUM_OF_MEM_KEY = 'num_of_mem'
MEM_INFO_START_ADDR_KEY = 'start_addr'
MEM_INFO_END_ADDR_KEY = 'end_addr'

# maximum data segment length
MAX_DATA_SEG_LEN = 32


# target device password
passwd= ['M', 'Y', 'P', 'A', 'S', 'S', 'W', 'D']

#===============================================================================
# OpenBSL Host class
#===============================================================================
class OpenBSLHost:
    #---------------------------------------------------------------------------
    # Class variables
    #---------------------------------------------------------------------------
    # serial port name
    serial_port_name = ""
    # flag for verbose mode
    verbose_mode = False
    # serial port handle
    serial_port = 0
    # mem info
    mem_info = {}
    # parser object
    parser = 0

    #---------------------------------------------------------------------------
    # Class functions
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    # init function - instantiation operation
    #---------------------------------------------------------------------------
    def __init__(self, serial_port_name, verbose):
        # save com port name, file name, and verbose mode
        self.serial_port_name = serial_port_name
        self.verbose_mode = verbose
        # create new instance of TI-TXT class
        self.parser = TiTxtParser(False)
        pass

    #---------------------------------------------------------------------------
    # setting serial port name
    #---------------------------------------------------------------------------
    def set_serial_port_name(self, port_name):
        self.serial_port_name = port_name
        pass

    #---------------------------------------------------------------------------
    # setting verbose mode
    #---------------------------------------------------------------------------
    def set_verbose_mode(self, verbose):
        self.verbose_mode = verbose
        pass

    #---------------------------------------------------------------------------
    # print error message
    #---------------------------------------------------------------------------
    def print_error(self, error):
        # change to int type if necessary
        if(type(error) == str):
            error_code = ord(error)
        else:
            error_code = error
        # decode the error code
        if(error_code == OPEN_BSL_RESP_ERR_UNKNOWN_CMD):
            print "ERROR CODE: Unknown Command"
        elif(error_code == OPEN_BSL_RESP_ERR_UNSUPPORTED_CMD):
            print "ERROR CODE: Unsupported Command"
        elif(error_code == OPEN_BSL_RESP_ERR_PASSWORD_PROTECTED):
            print "ERROR CODE: Command is password protected"
        elif(error_code == OPEN_BSL_RESP_ERR_INVALID_PARAM):
            print "ERROR CODE: Invalid command parameter"
        elif(error_code == OPEN_BSL_RESP_ERR_INVALID_FORMAT):
            print "ERROR CODE: Invalid command packet format"
        elif(error_code == OPEN_BSL_RESP_ERR_INVALID_CHECKSUM):
            print "ERROR CODE: Invalid command packet checksum"
        else:
            print "UNKNOWN ERROR CODE:", hex(error_code)

        pass

    #---------------------------------------------------------------------------
    # open serial port
    #---------------------------------------------------------------------------
    def open_serial_port(self):
        # try to open the serial-port
        try:
            if(self.verbose_mode == True):
                print "Opening Serial Port:", self.serial_port_name
            self.serial_port = serial.Serial(self.serial_port_name)
        except:
            if(self.verbose_mode == True):
                print "Failed to open serial port"
            return False

        # flush input output
        self.serial_port.flushOutput()
        self.serial_port.flushInput()

        return True

    #---------------------------------------------------------------------------
    # verify checksum in the given packet
    #---------------------------------------------------------------------------
    def verify_packet_checksum(self, pkt_len, packet):
        #init vars
        checksum = 0
        chksum_ok = False
        if((pkt_len > 0) and (len(packet) == pkt_len)):
            # calculate checksum
            for i in range(pkt_len-2):
                temp = checksum
                checksum = (temp >> 1)
                if(temp & 0x01):
                    checksum |= 0x8000
                checksum = checksum & 0xFFFF
                if(type(packet) == str):
                    checksum += ord(packet[i])
                else:
                    checksum += packet[i]
                checksum = checksum & 0xFFFF
            #print "CHECKSUM: ", hex(checksum)
            # get checksum field
            if(type(packet) == str):
                chksum_pkt = (ord(packet[pkt_len-1])*256) + ord(packet[pkt_len-2])
            else:
                chksum_pkt = (packet[pkt_len-1]*256) + packet[pkt_len-2]
            # compare
            if(chksum_pkt == checksum):
                chksum_ok = True
        return chksum_ok

    #---------------------------------------------------------------------------
    # verify checksum for given data
    #---------------------------------------------------------------------------
    def verify_checksum(self, data, calculated_chksum):
        #init vars
        checksum = 0
        chksum_ok = False
        # calculate checksum
        for i in range(len(data)):
            temp = checksum
            checksum = (temp >> 1)
            if(temp & 0x01):
                checksum |= 0x8000
            checksum = checksum & 0xFFFF
            if(type(data) == str):
                checksum += ord(data[i])
            else:
                checksum += data[i]
            checksum = checksum & 0xFFFF


        # compare
        #print "CHECKSUM: ", hex(checksum)
        if(calculated_chksum == checksum):
            if(self.verbose_mode == True):
                print "Matched checksum:", hex(checksum)
            chksum_ok = True
        else:
            if(self.verbose_mode == True):
                print "Unmatched checksum:", hex(checksum),"-", hex(calculated_chksum)

        return chksum_ok

    #---------------------------------------------------------------------------
    # update checksum value
    #---------------------------------------------------------------------------
    def update_checksum(self, byte, checksum):
        temp = checksum

        # shift right
        checksum = (temp >> 1)

        # remove carry from shift right operation to MSB
        if(temp & 0x01):
            checksum |= 0x8000
        checksum = checksum & 0xFFFF
        if(type(byte) == str):
            checksum += ord(byte)
        else:
            checksum += byte
        checksum = checksum & 0xFFFF

        return checksum

    #---------------------------------------------------------------------------
    # send OPEN_BSL_CMD_SYNC command until getting OK response
    #---------------------------------------------------------------------------
    def synchronize(self):
        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return False

        # init variables
        sync_ed = False
        retry = 0
        self.serial_port.timeout = 0.05

        # send SYNC command
        if(self.verbose_mode == True):
            print "Trying to send SYNC byte (", hex(OPEN_BSL_CMD_SYNC),")",
        while((retry < MAX_SYNC_RETRY) and (sync_ed == False)):
            # flush buffers
            self.serial_port.flushOutput()
            self.serial_port.flushInput()
            #send command
            self.serial_port.write(('' + chr(OPEN_BSL_CMD_SYNC)))
            # wait for reply
            byte = self.serial_port.read()
            try:
                if(ord(byte) == OPEN_BSL_RESP_OK):
                    if(self.verbose_mode == True):
                        print "- received OPEN_BSL_RESP_OK -> SUCCESS"
                    sync_ed = True
            except:
                sync_ed = False

        if(sync_ed == False) and (self.verbose_mode == True):
            print "- no OPEN_BSL_RESP_OK received -> ERROR"

        return sync_ed

    #---------------------------------------------------------------------------
    # opening password protected commands by sending OPEN_BSL_CMD_PASSWD command
    # with given password parameter
    #---------------------------------------------------------------------------
    def send_password(self, password):
        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return False

        # check password length
        pwd_len = OPEN_BSL_CMD_PASSWD_LEN - OPEN_BSL_CHKSUM_LEN
        if (len(password) != pwd_len):
            if(self.verbose_mode == True):
            	print "Invalid password length (must be", pwd_len, "bytes)"
            return False

        try:
            # send the request
            if(self.verbose_mode == True):
                print "Sending OPEN_BSL_CMD_PASSWD byte (", hex(OPEN_BSL_CMD_PASSWD),")"
            self.serial_port.write(('' + chr(OPEN_BSL_CMD_PASSWD)))

            # send password bytes
            checksum = 0
            for pwd_byte in password:
                # send single byte
                if(type(pwd_byte) != str):
                    self.serial_port.write(('' + chr(pwd_byte)))
                else:
                    self.serial_port.write(pwd_byte)
                # update checksum
                checksum = self.update_checksum(pwd_byte, checksum)

            # send the checksum bytes - LSB first
            self.serial_port.write(('' + chr( (checksum & 0x00FF) )))
            self.serial_port.write(('' + chr( (checksum & 0xFF00) >> 8 )))

            # set timeout
            self.serial_port.timeout = 0.5

            # try to read the response
            resp_byte = self.serial_port.read()
            # check response header
            if( ord(resp_byte) == (OPEN_BSL_CMD_PASSWD | OPEN_BSL_RESP_BIT_MASK)):
                if(self.verbose_mode == True):
                    print "Received positive response (", hex(ord(resp_byte)),")"
                return True
            else:
                if(self.verbose_mode == True):
                    self.print_error(resp_byte)
                return False

        except:
            if(self.verbose_mode == True):
            	print "Exception while sending OPEN_BSL_CMD_PASSWD"
            return False

    #---------------------------------------------------------------------------
    # get device memory info by sending OPEN_BSL_CMD_GET_MEM_INFO command
    #---------------------------------------------------------------------------
    def get_mem_info(self):
        #init vars
        mem_info = {}

        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return mem_info

        # send the request
        if(self.verbose_mode == True):
            print "Sending OPEN_BSL_GET_MEM_INFO byte (", hex(OPEN_BSL_GET_MEM_INFO),")"
        self.serial_port.write(('' + chr(OPEN_BSL_GET_MEM_INFO)))

        # set timeout
        self.serial_port.timeout = 1

        try:
            # try to read the header resp
            resp_byte = self.serial_port.read()
            # check response header
            if( ord(resp_byte) == (OPEN_BSL_GET_MEM_INFO | OPEN_BSL_RESP_BIT_MASK)):
                # read number of memory sections
                num_of_mem = self.serial_port.read()
                mem_info[MEM_INFO_NUM_OF_MEM_KEY] = ord(num_of_mem)

                # calculate packet length
                len_byte = ord(num_of_mem) * 8 + OPEN_BSL_CHKSUM_LEN

                # read complete bytes based on length byte
                reply_pkt = self.serial_port.read(len_byte)

                # insert the num of mem byte to the beginning of packet
                reply_pkt = num_of_mem + reply_pkt

                # verify checksum
                if(self.verify_packet_checksum(len_byte + 1, reply_pkt) == True):
                    if(self.verbose_mode == True):
                        print "Received positive response (", hex(ord(resp_byte)),")"
                    # check packet length
                    if(len(reply_pkt) == 1 + (ord(num_of_mem)*8) + OPEN_BSL_CHKSUM_LEN):
                        idx = 1
                        for i in range (ord(num_of_mem)):
                            mem = {}
                            # first 4 bytes is start address - LSB first
                            mem[MEM_INFO_START_ADDR_KEY] = ord(reply_pkt[idx])
                            mem[MEM_INFO_START_ADDR_KEY] += ord(reply_pkt[idx+1]) << 8
                            mem[MEM_INFO_START_ADDR_KEY] += ord(reply_pkt[idx+2]) << 16
                            mem[MEM_INFO_START_ADDR_KEY] += ord(reply_pkt[idx+2]) << 24
                            idx += 4
                            # second 4 bytes is end address - LSB first
                            mem[MEM_INFO_END_ADDR_KEY] = ord(reply_pkt[idx])
                            mem[MEM_INFO_END_ADDR_KEY] += ord(reply_pkt[idx+1]) << 8
                            mem[MEM_INFO_END_ADDR_KEY] += ord(reply_pkt[idx+2]) << 16
                            mem[MEM_INFO_END_ADDR_KEY] += ord(reply_pkt[idx+2]) << 24
                            idx += 4
                            # add to main dictionary
                            mem_info[i] = mem
                else:
                    if(self.verbose_mode == True):
                        print "Invalid checksum!"
                    mem_info = {}
            else:
                if(self.verbose_mode == True):
                    self.print_error(resp_byte)
                mem_info = {}
        except:
            if(self.verbose_mode == True):
            	print "Exception while sending OPEN_BSL_GET_MEM_INFO"
            mem_info = {}

        # save mem info
        self.mem_info = mem_info

        return mem_info

    #---------------------------------------------------------------------------
    # erase device image by sending OPEN_BSL_CMD_ERASE_IMAGE command
    #---------------------------------------------------------------------------
    def erase_image(self, idx = 0xFF):
        # init var
        ret_val = False

        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return False

        # send the request
        if(self.verbose_mode == True):
            print "Sending OPEN_BSL_CMD_ERASE_IMAGE byte (", hex(OPEN_BSL_CMD_ERASE_IMAGE),")",
            print "- index:", hex(idx)
        self.serial_port.write(('' + chr(OPEN_BSL_CMD_ERASE_IMAGE)))
        self.serial_port.write(('' + chr(idx)))

        # set timeout
        self.serial_port.timeout = 2

        try:
            # try to read the header resp
            resp_byte = self.serial_port.read()
            # check response header
            if( ord(resp_byte) == (OPEN_BSL_CMD_ERASE_IMAGE | OPEN_BSL_RESP_BIT_MASK)):
                if(self.verbose_mode == True):
                    print "Received positive response (", hex(ord(resp_byte)),")"
                ret_val = True
            else:
                if(self.verbose_mode == True):
                    self.print_error(resp_byte)
        except:
            if(self.verbose_mode == True):
            	print "Exception while sending OPEN_BSL_CMD_ERASE_IMAGE"

        return ret_val

    #---------------------------------------------------------------------------
    # download device image by sending OPEN_BSL_CMD_DOWNLOAD_IMAGE command
    #---------------------------------------------------------------------------
    def download_image(self, idx, data):
        ret_val = False
        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return False

        # check if mem info has been retrieved from target
        if (self.mem_info == {}):
            if(self.verbose_mode == True):
            	print "Memory info hasn't been retrieved from target"
            return False

        # check for correct memory section index
        if(idx >= self.mem_info[MEM_INFO_NUM_OF_MEM_KEY]):
            if(self.verbose_mode == True):
            	print "Invalid memory section index:", idx, "- max:", (self.mem_info[MEM_INFO_NUM_OF_MEM_KEY]-1)
            return False

        # check if data length matches the memory section length
        image_len = self.mem_info[idx][MEM_INFO_END_ADDR_KEY] - self.mem_info[idx][MEM_INFO_START_ADDR_KEY] + 1
        if(len(data) != image_len):
            if(self.verbose_mode == True):
            	print "Invalid image data length:", len(data), "- expected:", image_len
            return False

        # send the command
        if(self.verbose_mode == True):
            print "Sending OPEN_BSL_CMD_DOWNLOAD_IMAGE byte (", hex(OPEN_BSL_CMD_DOWNLOAD_IMAGE),")"
        self.serial_port.write(('' + chr(OPEN_BSL_CMD_DOWNLOAD_IMAGE)))
        self.serial_port.write(('' + chr(idx)))

        # now we are ready to send data
        checksum = 0
        for byte in data:
            self.serial_port.write(('' + chr(byte)))
            time.sleep(0.01) # sleep to enable device writing bytes
            checksum = self.update_checksum(byte, checksum)

        # send the checksum bytes - LSB first
        self.serial_port.write(('' + chr( (checksum & 0x00FF) )))
        self.serial_port.write(('' + chr( (checksum & 0xFF00) >> 8 )))

        # set timeout
        self.serial_port.timeout = 1

        # try to read the header resp
        resp_byte = self.serial_port.read()
        # check response header
        if( ord(resp_byte) == (OPEN_BSL_CMD_DOWNLOAD_IMAGE | OPEN_BSL_RESP_BIT_MASK)):
            if(self.verbose_mode == True):
                print "Received positive response (", hex(ord(resp_byte)),")"
            ret_val = True
        else:
            if(self.verbose_mode == True):
                self.print_error(resp_byte)

        return ret_val

    #---------------------------------------------------------------------------
    # upload device image by sending OPEN_BSL_CMD_UPLOAD_IMAGE command
    #---------------------------------------------------------------------------
    def upload_image(self, idx = 0xFF):
        # init var
        image = {}

        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return image

        # check if mem info has been retrieved from target
        if (self.mem_info == {}):
            if(self.verbose_mode == True):
            	print "Memory info hasn't been retrieved from target"
            return image

        # send the request
        if(self.verbose_mode == True):
            print "Sending OPEN_BSL_CMD_UPLOAD_IMAGE byte (", hex(OPEN_BSL_CMD_UPLOAD_IMAGE),")",
            print "- index:", hex(idx)
        self.serial_port.write(('' + chr(OPEN_BSL_CMD_UPLOAD_IMAGE)))
        self.serial_port.write(('' + chr(idx)))

        # set timeout
        self.serial_port.timeout = 0.5

        try:
            if (idx != 0xFF):
                mem_sect = range(idx, idx+1)
            else:
                mem_sect = range(0, self.mem_info[MEM_INFO_NUM_OF_MEM_KEY])
            for i in mem_sect:
                # try to read the header resp
                resp_byte = self.serial_port.read()
                # check response header
                if( ord(resp_byte) == (OPEN_BSL_CMD_UPLOAD_IMAGE | OPEN_BSL_RESP_BIT_MASK)):
                    # read image section number:
                    mem_num = self.serial_port.read()
                    # start building image
                    start_addr = self.mem_info[i][MEM_INFO_START_ADDR_KEY]
                    end_addr = self.mem_info[i][MEM_INFO_END_ADDR_KEY]
                    len_mem = end_addr - start_addr + 1
                    if(self.verbose_mode == True):
                        print "Receiving image index:", ord(mem_num), "- Start Addr:", hex(start_addr), ", len:", hex(len_mem)
                    image[start_addr] = []
                    for j in range(len_mem+2):
                        # read the incoming bytes header resp
                        byte = self.serial_port.read()
                        image[start_addr].append(ord(byte))
                    # verify checksum
                    if(self.verify_packet_checksum(len_mem+2, image[start_addr]) != True):
                        if(self.verbose_mode == True):
                	       print "Wrong checksum!"
                        return {}
                    else:
                        if(self.verbose_mode == True):
                            print "Received positive response (", hex(ord(resp_byte)),")",
                            print "- for image index:", ord(mem_num)
                        # remove checksum
                        image[start_addr].pop()
                        image[start_addr].pop()
                else:
                    if(self.verbose_mode == True):
                        self.print_error(resp_byte)

        except:
            if(self.verbose_mode == True):
            	print "Exception while sending OPEN_BSL_CMD_UPLOAD_IMAGE"
            image = {}

        return image


    #---------------------------------------------------------------------------
    # calculate checksum by sending OPEN_BSL_CMD_CALCULATE_CHECKSUM command
    #---------------------------------------------------------------------------
    def calculate_checksum(self, start_addr, end_addr):
        # init variable
        chksum = 0

        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return image

        # send the request
        if(self.verbose_mode == True):
            print "Sending OPEN_BSL_CMD_CALCULATE_CHECKSUM byte (", hex(OPEN_BSL_CMD_CALCULATE_CHECKSUM),")",
            print "- StartAddr:", hex(start_addr), ", EndAddr:", hex(end_addr)
        self.serial_port.write(('' + chr(OPEN_BSL_CMD_CALCULATE_CHECKSUM)))

        # send start address
        byte = start_addr & 0xFF # byte 0
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF00) >> 8 # byte 1
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF0000) >> 16 # byte 2
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF000000) >> 24 # byte 3
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)

        # send end address
        byte = end_addr & 0xFF # byte 0
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (end_addr & 0xFF00) >> 8 # byte 1
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (end_addr & 0xFF0000) >> 16 # byte 2
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (end_addr & 0xFF000000) >> 24 # byte 3
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)

        # send the checksum bytes - LSB first
        self.serial_port.write(('' + chr( (chksum & 0x00FF) )))
        self.serial_port.write(('' + chr( (chksum & 0xFF00) >> 8 )))

        # set timeout
        self.serial_port.timeout = 2

        try:
            # try to read the header resp
            resp_byte = self.serial_port.read()
            # check response header
            if( ord(resp_byte) == (OPEN_BSL_CMD_CALCULATE_CHECKSUM | OPEN_BSL_RESP_BIT_MASK)):
                # read the calculate checksum
                chksum = ord(self.serial_port.read())
                chksum += ord(self.serial_port.read()) * 256
                if(self.verbose_mode == True):
                    print "Received positive response (", hex(ord(resp_byte)),")",
                    print "- Checksum:", hex(chksum)
            else:
                if(self.verbose_mode == True):
                    self.print_error(resp_byte)
        except:
            if(self.verbose_mode == True):
            	print "Exception while sending OPEN_BSL_CMD_CALCULATE_CHECKSUM"
            chksum = 0

        return chksum



    #---------------------------------------------------------------------------
    # erase device memory segment by sending OPEN_BSL_CMD_ERASE_SEGMENT command
    #---------------------------------------------------------------------------
    def erase_segment(self, start_addr, end_addr):
        # init variable
        ret_val = True
        chksum = 0

        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return image

        # send the request
        if(self.verbose_mode == True):
            print "Sending OPEN_BSL_CMD_ERASE_SEGMENT byte (", hex(OPEN_BSL_CMD_ERASE_SEGMENT),")",
            print "- StartAddr:", hex(start_addr), ", EndAddr:", hex(end_addr)
        self.serial_port.write(('' + chr(OPEN_BSL_CMD_ERASE_SEGMENT)))

        # send start address
        byte = start_addr & 0xFF # byte 0
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF00) >> 8 # byte 1
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF0000) >> 16 # byte 2
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF000000) >> 24 # byte 3
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)

        # send end address
        byte = end_addr & 0xFF # byte 0
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (end_addr & 0xFF00) >> 8 # byte 1
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (end_addr & 0xFF0000) >> 16 # byte 2
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (end_addr & 0xFF000000) >> 24 # byte 3
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)

        # send the checksum bytes - LSB first
        self.serial_port.write(('' + chr( (chksum & 0x00FF) )))
        self.serial_port.write(('' + chr( (chksum & 0xFF00) >> 8 )))

        # set timeout
        self.serial_port.timeout = 2

        try:
            # try to read the header resp
            resp_byte = self.serial_port.read()
            # check response header
            if( ord(resp_byte) == (OPEN_BSL_CMD_ERASE_SEGMENT | OPEN_BSL_RESP_BIT_MASK)):
                if(self.verbose_mode == True):
                    print "Received positive response (", hex(ord(resp_byte)),")"
            else:
                if(self.verbose_mode == True):
                    self.print_error(resp_byte)
                ret_val = False
        except:
            if(self.verbose_mode == True):
            	print "Exception while sending OPEN_BSL_CMD_ERASE_SEGMENT"
            ret_val = False


        return ret_val

    #---------------------------------------------------------------------------
    # upload segment command
    #---------------------------------------------------------------------------
    def upload_segment(self, start_addr, end_addr):
        # init var
        data = []
        chksum = 0

        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return data

        # send the request
        if(self.verbose_mode == True):
            print "Sending OPEN_BSL_CMD_UPLOAD_SEGMENT byte (", hex(OPEN_BSL_CMD_UPLOAD_SEGMENT),")"
        self.serial_port.write(('' + chr(OPEN_BSL_CMD_UPLOAD_SEGMENT)))

        # send start address
        byte = start_addr & 0xFF # byte 0
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF00) >> 8 # byte 1
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF0000) >> 16 # byte 2
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF000000) >> 24 # byte 3
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)

        # send end address
        byte = end_addr & 0xFF # byte 0
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (end_addr & 0xFF00) >> 8 # byte 1
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (end_addr & 0xFF0000) >> 16 # byte 2
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (end_addr & 0xFF000000) >> 24 # byte 3
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)

        # send the checksum bytes - LSB first
        self.serial_port.write(('' + chr( (chksum & 0x00FF) )))
        self.serial_port.write(('' + chr( (chksum & 0xFF00) >> 8 )))

        # set timeout
        self.serial_port.timeout = 0.5

        try:
            # try to read the header resp
            resp_byte = self.serial_port.read()
            # check response header
            if( ord(resp_byte) == (OPEN_BSL_CMD_UPLOAD_SEGMENT | OPEN_BSL_RESP_BIT_MASK)):
                # read length:
                len_pckt = self.serial_port.read()
                upload_len = end_addr - start_addr + 1
                if (ord(len_pckt) == upload_len + OPEN_BSL_CHKSUM_LEN):
                    chksum = 0
                    # collect the data bytes
                    for i in range(upload_len):
                        byte = ord(self.serial_port.read())
                        data.append(byte)
                        chksum = self.update_checksum(byte, chksum)
                    # remove checksum
                    rcv_chksum = ord(self.serial_port.read())
                    rcv_chksum += ord(self.serial_port.read()) * 256
                    if(rcv_chksum != chksum):
                        if(self.verbose_mode == True):
                	       print "Wrong checksum:", hex(rcv_chksum), "- expected: ", hex(chksum)
                        data = []
                    else:
                        if(self.verbose_mode == True):
                            print "Received positive response (", hex(ord(resp_byte)),")"
                else:
                    if(self.verbose_mode == True):
            	       print "Unexpected packet length:", len_pckt, "- expected: ", (upload_len+OPEN_BSL_CHKSUM_LEN)

            else:
                if(self.verbose_mode == True):
                    self.print_error(resp_byte)

        except:
            if(self.verbose_mode == True):
            	print "Exception while sending OPEN_BSL_CMD_UPLOAD_SEGMENT"
            data = []

        return data

    #---------------------------------------------------------------------------
    # download segment command
    #---------------------------------------------------------------------------
    def download_segment(self, start_addr, data):
        # init var
        ret_val = False
        chksum = 0

        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return data

        # check parameter
        max_data_len = 255 - OPEN_BSL_CHKSUM_LEN - 4
        if(len(data) >= max_data_len):
            if(self.verbose_mode == True):
                print "Invalid data length:", len(data),"- max:", max_data_len
            return False

        # send the request
        if(self.verbose_mode == True):
            print "Sending OPEN_BSL_CMD_DOWNLOAD_SEGMENT byte (", hex(OPEN_BSL_CMD_DOWNLOAD_SEGMENT),")",
            print "- data length:", len(data)
        self.serial_port.write(('' + chr(OPEN_BSL_CMD_DOWNLOAD_SEGMENT)))

        # send packet length
        pckt_len = len(data) + OPEN_BSL_CHKSUM_LEN + 4
        self.serial_port.write(('' + chr(pckt_len)))

        # send start address
        byte = start_addr & 0xFF # byte 0
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF00) >> 8 # byte 1
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF0000) >> 16 # byte 2
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)
        byte = (start_addr & 0xFF000000) >> 24 # byte 3
        self.serial_port.write(('' + chr(byte)))
        chksum = self.update_checksum(byte, chksum)

        # send the data bytes
        for byte in data:
            self.serial_port.write(('' + chr(byte)))
            time.sleep(0.01) # sleep to enable device writing bytes
            chksum = self.update_checksum(byte, chksum)

        # send the checksum bytes - LSB first
        self.serial_port.write(('' + chr( (chksum & 0x00FF) )))
        self.serial_port.write(('' + chr( (chksum & 0xFF00) >> 8 )))

        # set timeout
        self.serial_port.timeout = 0.5

        try:
            # try to read the header resp
            resp_byte = self.serial_port.read()
            # check response header
            if( ord(resp_byte) == (OPEN_BSL_CMD_DOWNLOAD_SEGMENT | OPEN_BSL_RESP_BIT_MASK)):
                ret_val= True
                if(self.verbose_mode == True):
                    print "Received positive response (", hex(ord(resp_byte)),")"
            else:
                if(self.verbose_mode == True):
                    self.print_error(resp_byte)

        except:
            if(self.verbose_mode == True):
            	print "Exception while sending OPEN_BSL_CMD_DOWNLOAD_SEGMENT"

        return ret_val


    #---------------------------------------------------------------------------
    # run application by sending OPEN_BSL_CMD_RUN_APP command
    #---------------------------------------------------------------------------
    def run_application(self, idx = 0xFF):
        # init var
        ret_val = False

        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return False

        # send the request
        if(self.verbose_mode == True):
            print "Sending OPEN_BSL_CMD_RUN_APP byte (", hex(OPEN_BSL_CMD_RUN_APP),")",
            print "- index:", hex(idx)
        self.serial_port.write(('' + chr(OPEN_BSL_CMD_RUN_APP)))

        # set timeout
        self.serial_port.timeout = 0.1

        try:
            # try to read the header resp
            resp_byte = self.serial_port.read()
            # check response header
            if( ord(resp_byte) == (OPEN_BSL_CMD_RUN_APP | OPEN_BSL_RESP_BIT_MASK)):
                if(self.verbose_mode == True):
                    print "Received positive response (", hex(ord(resp_byte)),")"
                ret_val = True
            else:
                if(self.verbose_mode == True):
                    self.print_error(resp_byte)
        except:
            if(self.verbose_mode == True):
            	print "Exception while sending OPEN_BSL_CMD_RUN_APP"

        return ret_val


    #---------------------------------------------------------------------------
    # flash_image_segment_wise
    #---------------------------------------------------------------------------
    def flash_image_segment_wise(self, file_name, check_img_checksum = False):
        # init var
        ret_val = False

        # check if serial port has been initialized
        if (self.serial_port == 0):
            if(self.verbose_mode == True):
            	print "Serial Port hasn't been initialized"
            return data

        # parse the image
        image = self.parser.parse(file_name)
        if(image == {}):
            if(self.verbose_mode == True):
            	print "Failed to parser input file:", file_name
            return ret_val

        # get the starting address of the image
        start_addrs = image.keys()
        for addr in start_addrs:
            i = 0
            curr_addr = addr
            # get section length
            sect_len = len (image[addr])
            while (i < sect_len):
                # get data to be downloaded
                data_len_left = sect_len - i
                data_len = min(data_len_left, MAX_DATA_SEG_LEN)
                data = []
                for idx in range(i, (i+data_len)):
                    data.append(image[addr][idx])
                # download segment
                if(self.download_segment(curr_addr, data) != True):
                    if(self.verbose_mode == True):
                    	print "Failed to download segment starting from addr:", hex(addr)
                    return ret_val
                # update index and address parameter
                i = i + data_len
                curr_addr = curr_addr + data_len

        # check image checksum if necessary
        if(check_img_checksum != False):
            # get the starting address of the image
            start_addrs = image.keys()
            for addr in start_addrs:
                # get section length
                len_section = len(image[addr])
                end_addr = addr + len_section - 1
                if(self.verbose_mode == True):
                	print "Checking image checksum from address:", hex(addr), "-", hex(end_addr)
                # ask device to calculate checksum for particular section
                dev_chksum = self.calculate_checksum(addr, end_addr)
                # verify the checksum
                if(self.verify_checksum(image[addr], dev_chksum) != True):
                    if(self.verbose_mode == True):
                    	print "Unmatched checksum at section:", hex(addr),"-", hex(end_addr)
                        return ret_val

        # all data has been successfully downloaded
        ret_val = True

        return ret_val


#---------------------------------------------------------------------------
# do test for MSP430G2553 target
#---------------------------------------------------------------------------
def test_msp430g2553(port_name, verbose_mode):
    # create new instance of OpenBSL Host
    print "\r\n* Creating new instance of OpenBSL Host"
    openbsl = OpenBSLHost(port_name, verbose_mode)

    # open BSL host
    print "\r\n* Opening Serial Port"
    if (openbsl.open_serial_port() != True):
        print "ERROR: Failed to open serial port ", options.serial_port_name
        sys.exit(1)

    # try to send SYNC
    print "\r\n* Sychronizing with BSL device"
    if(openbsl.synchronize() != True):
        print "ERROR: Failed to synchronize with BSL"
        sys.exit(1)

    # send password
    print "\r\n* Opening password protected commands"
    if(openbsl.send_password(passwd) != True):
        print "ERROR: Failed to open password protected commands"
        sys.exit(1)

    # try to get memory information
    print "\r\n* Getting BSL device memory info"
    mem_info = openbsl.get_mem_info()
    if(mem_info != {}):
        print "Device Memory Information: Num Of Mem Sections =", mem_info['num_of_mem']
        for i in range(mem_info[MEM_INFO_NUM_OF_MEM_KEY]):
            print "  Section (", i, ")"
            print "     Start Address : ", hex(mem_info[i][MEM_INFO_START_ADDR_KEY])
            print "     End Address   : ", hex(mem_info[i][MEM_INFO_END_ADDR_KEY])
    else:
        print "ERROR: Failed getting device memory information"
        sys.exit(1)

    # erasing all device memory image
    print "\r\n* Erasing BSL device memory image"
    if(openbsl.erase_image() != True):
        print "ERROR: Failed to erase memory image"
        sys.exit(1)

    # try to upload image
    print "\r\n* Uploading BSL device memory image"
    image = openbsl.upload_image()
    if(image != {}):
        res = openbsl.parser.print_ti_txt("full_image_0.txt", image)
        if (res != True):
            print "ERROR: Failed to write output filled TI-TXT file!"
            sys.exit(1)
    else:
            print "ERROR: Failed to upload image!"
            sys.exit(1)

    # write new image at mem section 0
    new_image = []
    for i in range(len(image[image.keys()[0]])):
        new_image.append(i)
    print "\r\n* Downloading BSL device memory image 0"
    if(openbsl.download_image(0, new_image) != True):
        print "ERROR: Failed to download image!"
        sys.exit(1)

    # upload image from mem section 0
    print "\r\n* Uploading BSL device memory image 0"
    image = openbsl.upload_image(0)
    if(image != {}):
        res = openbsl.parser.print_ti_txt("image_0.txt", image)
        if (res != True):
            print "ERROR: Failed to write output filled TI-TXT file!"
            sys.exit(1)
    else:
            print "ERROR: Failed to upload image!"
            sys.exit(1)

    # compare image
    if(new_image != image[image.keys()[0]]):
        print "ERROR: Image unmatched!"
        sys.exit(1)

    # send command with wrong image number
    print "\r\n* Erasing BSL device memory image number:", mem_info[MEM_INFO_NUM_OF_MEM_KEY],
    print "- shall return ERROR"
    if(openbsl.erase_image(mem_info[MEM_INFO_NUM_OF_MEM_KEY]+1) != False):
        print "ERROR: Command with wrong image number succeeds"
        sys.exit(1)

    # try to send SYNC
    print "\r\n* Sychronizing with BSL device"
    if(openbsl.synchronize() != True):
        print "ERROR: Failed to synchronize with BSL"
        sys.exit(1)

    # send command with wrong image number
    print "\r\n* Uploading BSL device memory image number:", mem_info[MEM_INFO_NUM_OF_MEM_KEY],
    print "- shall return ERROR"
    if(openbsl.upload_image(mem_info[MEM_INFO_NUM_OF_MEM_KEY]+1) != {}):
        print "ERROR: Command with wrong image number succeeds"
        sys.exit(1)

    # try to send SYNC
    print "\r\n* Sychronizing with BSL device"
    if(openbsl.synchronize() != True):
        print "ERROR: Failed to synchronize with BSL"
        sys.exit(1)

    # send calculate checksum command
    print "\r\n* Calculating checksum BSL device memory image 0"
    start_addr = mem_info[0][MEM_INFO_START_ADDR_KEY]
    end_addr = mem_info[0][MEM_INFO_END_ADDR_KEY]
    chksum = openbsl.calculate_checksum(start_addr, end_addr)
    if(openbsl.verify_checksum(new_image, chksum) != True):
        print "ERROR: Wrong calculated checksum!"
        sys.exit(1)

    # send erase segment command
    start_addr = mem_info[0][MEM_INFO_START_ADDR_KEY]
    end_addr = mem_info[0][MEM_INFO_START_ADDR_KEY] + 63
    print "\r\n* Erasing Segment"
    if(openbsl.erase_segment(start_addr, end_addr) != True):
        print "ERROR: Failed to erase segment!"
        sys.exit(1)

    # send erase segment command
    print "\r\n* Upload Segment"
    data_segment = openbsl.upload_segment(start_addr, end_addr)
    if(data_segment == []):
        print "ERROR: Failed to upload segment!"
        sys.exit(1)
    pass

    # upload image from mem section 0
    print "\r\n* Uploading BSL device memory image 0"
    image = openbsl.upload_image(0)
    if(image != {}):
        res = openbsl.parser.print_ti_txt("image_1.txt", image)
        if (res != True):
            print "ERROR: Failed to write output filled TI-TXT file!"
            sys.exit(1)
    else:
            print "ERROR: Failed to upload image!"
            sys.exit(1)

    # re-write data segment
    for i in range(len(data_segment)):
        data_segment[i] = 0x80 + i
    print "\r\n* Download Segment"
    if(openbsl.download_segment(start_addr, data_segment) != True):
        print "ERROR: Failed to download segment!"
        sys.exit(1)

    # upload image from mem section 0
    print "\r\n* Uploading BSL device memory image 0"
    image = openbsl.upload_image(0)
    if(image != {}):
        res = openbsl.parser.print_ti_txt("image_2.txt", image)
        if (res != True):
            print "ERROR: Failed to write output filled TI-TXT file!"
            sys.exit(1)
    else:
            print "ERROR: Failed to upload image!"
            sys.exit(1)

    print "\r\n* Test for MSP430G2553 succeeds"
    pass

#===============================================================================
# main script
#===============================================================================
if __name__ == '__main__':
    # check python version
    #python_version = sys.version_info
    #if (python_version[0] != 2) and (python_version[1] != 6):
    #    print "WARNING: script has been only tested with Python 2.6"

    #parse the command line parameters using OptionParser
    cmd_line_parser = optparse.OptionParser()
    cmd_line_parser.add_option("-v", "--verbose", action="store_true",
            dest="verbose", help="activate verbose mode")
    cmd_line_parser.add_option("-p", "--port", action="store", type="string",
            dest="serial_port_name", help="serial port name with name PORT",
            metavar="PORT")
    cmd_line_parser.add_option("-t", "--test", action="store_true",
            dest="test", help="test for MSP430G2553 target device")
    cmd_line_parser.add_option("-i", "--infile", action="store", type="string",
            dest="input_file_name", help="input file name in TI TXT format for flashing target device",
            metavar="INFILE")
    cmd_line_parser.add_option("-o", "--outfile", action="store", type="string",
            dest="output_file_name", help="output file name in TI TXT format for reading target device",
            metavar="OUTFILE")
    (options, args) = cmd_line_parser.parse_args()

    # check mandatory parameter(s)
    if(options.serial_port_name == True):
        print "ERROR: Serial Port parameter is missing!"
        cmd_line_parser.print_help()
        sys.exit(1)

    # check if it is to run test
    if(options.test == True):
        # run test
        test_msp430g2553(options.serial_port_name, options.verbose)

    elif(options.input_file_name != None):
        # create new instance of OpenBSL Host
        print "\r\n* Creating new instance of OpenBSL Host"
        openbsl = OpenBSLHost(options.serial_port_name, options.verbose)

        # open BSL host
        print "\r\n* Opening Serial Port"
        if (openbsl.open_serial_port() != True):
            print "ERROR: Failed to open serial port ", options.serial_port_name
            sys.exit(1)

        # try to send SYNC
        print "\r\n* Sychronizing with BSL device"
        if(openbsl.synchronize() != True):
            print "ERROR: Failed to synchronize with BSL"
            sys.exit(1)

        # send password
        print "\r\n* Opening password protected commands"
        if(openbsl.send_password(passwd) != True):
            print "ERROR: Failed to open password protected commands"
            sys.exit(1)

        # erase image
        print "\r\n* Erasing device image"
        if(openbsl.erase_image() != True):
            print "ERROR: Failed to erase image"
            sys.exit(1)

        # flash image
        print "\r\n* Flashing image from input file:", options.input_file_name
        if(openbsl.flash_image_segment_wise(options.input_file_name, True) != True):
            print "ERROR: Failed to flash image into target device!"
            sys.exit(1)

        # try to read the checksum of the flashed image


        # start application
        print "\r\n* Starting application"
        if(openbsl.run_application() != True):
            print "ERROR: Failed to run application!"
            sys.exit(1)

    # exit
    sys.exit(0)
