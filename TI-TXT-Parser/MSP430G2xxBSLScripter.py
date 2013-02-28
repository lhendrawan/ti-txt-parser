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
# Name:        MSP430G2xxBslScripter.py
#
# Description: BSL Scripter like python script for MSP430G2xx BSL as described
#              in SLAA450 Application Notea of Texas Instruments
#
# Author:      Leo Hendrawan
#
# Version:     0.2
#
# Licence:     BSD license
#
# Note:        This module requires pyserial (http://pyserial.sourceforge.net/)
#
# Log:
#     - Version 0.1 (2013.02.22) :
#       Hello World! (created)
#     - Version 0.2 (yyyy.mm.dd) :
#       minor modification to suit TiTxtParser v0.2
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
CMD_SYNC = 0xBA
ACK = 0xF8
NACK = 0xFE
SLEEP_1MS = 0.001 # 1ms

#===============================================================================
# MSP430G2xxBslScripter class
#===============================================================================
class MSP430G2xxBslScripter:
    #---------------------------------------------------------------------------
    # Class variables
    #---------------------------------------------------------------------------
    # file name of TI-TXT file to be parsed
    file_name = ""
    # flag for verbose mode
    verbose_mode = False
    # TI-TXT content (dictionary)
    serial_port = ""
    # start address of device target flash memory
    start_addr = 0

    #---------------------------------------------------------------------------
    # Class functions
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    # init function - instantiation operation
    #---------------------------------------------------------------------------
    def __init__(self, serial_port, file, start, verbose):
        # save com port name, file name, and verbose mode
        self.serial_port = serial_port
        self.file_name = file
        self.start_addr = start
        self.verbose_mode = verbose

    #---------------------------------------------------------------------------
    # setting com port name
    #---------------------------------------------------------------------------
    def set_input_file(self, com):
        self.com_port = com

    #---------------------------------------------------------------------------
    # setting input file name
    #---------------------------------------------------------------------------
    def set_input_file(self, input_file):
        self.file_name = input_file

    #---------------------------------------------------------------------------
    # setting verbose mode
    #---------------------------------------------------------------------------
    def set_verbose_mode(self, verbose):
        self.verbose_mode = verbose

    #---------------------------------------------------------------------------
    # flash target device
    #---------------------------------------------------------------------------
    def flash_target(self):
        # create new instance of TI-TXT class
        ti_txt = TiTxtParser(self.verbose_mode)

        # parse the TI-TXT
        content = ti_txt.parse(self.file_name)
        if(content == {}):
            if(self.verbose_mode == True):
                print "Failed to parse TI-TXT file:", options.file_name
            return False
        #ti_txt.debug_print_content()

        # try to fill the data
        full_content = ti_txt.fill(content, self.start_addr, 0xFFFF, 0xFF)
        if(full_content == {}):
            if(self.verbose_mode == True):
                print "Failed to fill TI-TXT file"
            return False
        #ti_txt.debug_print_full_content(full_content)

        if(self.verbose_mode == True):
            print "\n== Flashing Target Device =="

        # try to open the serial-port
        try:
            if(self.verbose_mode == True):
                print "Opening Serial Port:", self.serial_port
            ser = serial.Serial(self.serial_port)
        except:
            if(self.verbose_mode == True):
                print "Failed to open serial port"
            return False

        # flush input output
        ser.flushInput()
        ser.flushOutput()

        # send CMD_SYNC byte
        if(self.verbose_mode == True):
            print "Sending SYNC byte (", hex(CMD_SYNC),")"
        ser.write(('' + chr(CMD_SYNC)))
        time.sleep(SLEEP_1MS * 100) # device needs time to rewrite int.vector

        # send the data bytes and calculate checksum while sending
        if(self.verbose_mode == True):
            data_len = len(range(self.start_addr, 0xFFFE))
            print "Sending binary data - length:", data_len, "(",
            print hex(data_len), ") bytes"
        chksum = 0
        for addr in range(self.start_addr, 0xFFFE):
            byte = full_content[self.start_addr][addr-self.start_addr]
            ser.write(('' + chr(byte)))
            time.sleep(SLEEP_1MS * 5) # sleep 5 ms between sending bytes
            chksum ^= byte

        # send checksum
        if(self.verbose_mode == True):
            print "Sending checksum byte (", hex(chksum),")"
        ser.write(('' + chr(chksum)))
        time.sleep(SLEEP_1MS * 5) # sleep 5 ms between sending bytes

        # wait for reply
        if(self.verbose_mode == True):
        	print "Reading reply from target"
        byte = ser.read()
        ser.close()
        if(byte == chr(ACK)):
            if(self.verbose_mode == True):
                print "received ACK"
            return True
        else:
            if(self.verbose_mode == True):
            	print "received NACK"
            return False

#===============================================================================
# main script
#===============================================================================
if __name__ == '__main__':
    #parse the command line parameters using OptionParser
    cmd_line_parser = optparse.OptionParser()
    cmd_line_parser.add_option("-f", "--file", action="store", type="string",
            dest="file_name", help="TI-TXT input file with name FILE",
            metavar="FILE")
    cmd_line_parser.add_option("-v", "--verbose", action="store_true",
            dest="verbose", help="actiate verbose mode")
    cmd_line_parser.add_option("-p", "--port", action="store", type="string",
            dest="serial_port", help="serial port name with name PORT",
            metavar="PORT")
    cmd_line_parser.add_option("-s", "--start", action="store", type="int",
            dest="start_addr", help="flash start address with value of SADDR",
            metavar="SADDR")
    (options, args) = cmd_line_parser.parse_args()

    # check given input file name parameter
    if(options.file_name == None):
        print "Input TI-TXT file name is missing!"
        cmd_line_parser.print_help()
        sys.exit(1)
    elif(options.serial_port == None):
        print "Serial port name is missing!"
        cmd_line_parser.print_help()
        sys.exit(1)
    elif(options.start_addr == None):
        print "Device flash start address is missing!"
        cmd_line_parser.print_help()
        sys.exit(1)

    # create new instance of TI-TXT class
    bsl = MSP430G2xxBslScripter(options.serial_port, options.file_name,
                options.start_addr, options.verbose)

    # flash target device
    result = bsl.flash_target()
    if(result == False):
        print "Fail to flash target device!"

    # exit
    sys.exit(0)
