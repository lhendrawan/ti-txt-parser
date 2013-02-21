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
# Name:        TiTxtParser.py
#
# Description: TI-TXT file parser
#
# Author:      Leo Hendrawan
#
# Version:     0.1
#
# Licence:     New BSD license
#
# Note:
#
# Log:
#     - Version 0.1 (2013.02.21) :
#       Hello World! (created)
#
#===============================================================================
#!/usr/bin/env python

import sys
import optparse

#===============================================================================
# TI-TXT class
#===============================================================================
class TiTxtParser:
    #---------------------------------------------------------------------------
    # Class variables
    #---------------------------------------------------------------------------
    # file name of TI-TXT file to be parsed
    file_name = ""
    # flag for verbose mode
    verbose_mode = False
    # TI-TXT content (dictionary)
    content = {}

    #---------------------------------------------------------------------------
    # Class functions
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    # init function - instantiation operation
    #---------------------------------------------------------------------------
    def __init__(self, file, verbose):
        # save file name and verbose mode
        self.file_name = file
        self.verbose_mode = verbose

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
    # get start address in TI-TXT file content
    #---------------------------------------------------------------------------
    def get_start_addr(self):
        start_addr = -1
        for addr in self.content.keys():
            if(start_addr == -1):
                # first iteration
                start_addr = addr
            else:
                if(addr < start_addr):
                    # save new start address
                    start_addr = addr
        return start_addr

    #---------------------------------------------------------------------------
    # get end address in TI-TXT file content
    #---------------------------------------------------------------------------
    def get_end_addr(self):
        end_addr = -1
        for addr in self.content.keys():
            if(end_addr == -1):
                # first iteration
                end_addr = addr
            else:
                if(addr > end_addr):
                    # save new end address
                    end_addr = addr

        # add the length
        if(end_addr != -1):
            end_addr += len(self.content[end_addr]) - 1
        return end_addr

    #---------------------------------------------------------------------------
    # parse the TI-TXT file
    #---------------------------------------------------------------------------
    def parse(self):
        # try to open input file
        try:
            if(self.verbose_mode == True):
                print "\nOpening TI-TXT File: ", self.file_name
            file = open(self.file_name, 'r')
        except:
            if(self.verbose_mode == True):
                print "\nError in opening TI-TXT file ", self.file_name
            return {}

        # start parsing
        for line in file:
            # check if this is a start address line
            if(line.find('@') != -1):
                try:
                    # add new entry in dictinary
                    addr_num = line.lstrip('@')
                    start_addr = int(addr_num,16)
                    self.content[start_addr] = []
                    if(self.verbose_mode == True):
                        print "Parsing data starting from address",
                        print hex(start_addr), "(", start_addr, ")"
                except:
                    if(self.verbose_mode == True):
                        print "Error while parsing: ", line
                    file.close()
                    return {}

            # check if this is not end line
            elif(line != 'q\n'):
                # split the strings into array of byte strings
                byte_line = line.split(' ')
                for byte_str in byte_line:
                    try:
                        if(byte_str != '\n'):
                            # convert byte string to integer value
                            byte_int = int(byte_str, 16)
                            # append in the array
                            self.content[start_addr].append(byte_int)
                    except:
                        if(self.verbose_mode == True):
                            print "Error while trying to convert: ", byte_str
                        file.close()
                        return {}

        # close file
        file.close()

        # return content as dictionary
        return self.content

    #---------------------------------------------------------------------------
    # file the empty memory of TI-TXT file content
    #---------------------------------------------------------------------------
    def fill(self, start_addr, end_addr, fill_byte):
        # initialize variable
        full_content = {}

        # check for starting and ending address
        if(start_addr > self.get_start_addr()):
            if(self.verbose_mode == True):
                print "Invalid Start Address: ", hex(start_addr),
                print " - TI-TXT content start address: ", self.get_start_addr()
            return {}
        elif(end_addr < self.get_end_addr()):
            if(self.verbose_mode == True):
                print "Invalid End Address: ", hex(end_addr),
                print " - TI-TXT content end address: ", self.get_end_addr()
            return {}

        # print start message
        if(self.verbose_mode == True):
            print "\nFilling memory range"
            print "Start Addr:", hex(start_addr)
            print "End Addr:", hex(end_addr)
            print "Fill byte ", hex(fill_byte)

        # now we can work - make a list of key addresses of the TI-TXT
        # original content
        addr_keys = self.content.keys()
        addr_keys.sort()

        # create the key for dictionary and value as array
        full_content[start_addr] = []

        # fill the empty memory between start address and the first address
        # in the key addresses
        addr_idx = start_addr
        for addr in addr_keys:
            if(addr_idx != addr):
                if(self.verbose_mode == True):
                    print "Filling empty byte(s) from address", hex(addr_idx),
                    print "to address ", hex(addr)
                loop = range(addr_idx, addr)
                for i in loop:
                    full_content[start_addr].append(fill_byte)
                    addr_idx += 1

            # append the content directly
            if(self.verbose_mode == True):
                print "Copying ", len(self.content[addr]),
                print "bytes data from address ", hex(addr)
            for byte in self.content[addr]:
                full_content[start_addr].append(byte)
            # update start address
            addr_idx += len(self.content[addr])

        # return
        return full_content

    #---------------------------------------------------------------------------
    # Debug print TI-TXT file content
    #---------------------------------------------------------------------------
    def debug_print_content(self):
        print "\nTI-TXT content:"
        #print TI-TXT content
        try:
            for entry_key in self.content.keys():
                print "Start Addr: ", hex(entry_key),
                print "len = ", len(self.content[entry_key])
                i = 0
                for bytes in self.content[entry_key]:
                    print "0x%02x" % bytes,
                    # print maximum 16 entries per line
                    i += 1
                    if(i == 16):
                        print ""
                        i = 0
                print ""
        except:
            print "Error while trying to print out TI-TXT content"

    #---------------------------------------------------------------------------
    # Debug print full (filled) TI-TXT file content
    #---------------------------------------------------------------------------
    def debug_print_full_content(self, full_content):
        start_addr = full_content.keys()[0]
        end_addr = start_addr + len(full_content[start_addr]) - 1
        try:
            print "\nFull content (length: ", len(full_content[start_addr]), "):"
            full_range = range (start_addr, end_addr+1)
            bytes = full_content[start_addr]
            idx = 0
            for addr in full_range:
                byte = bytes[(addr-start_addr)]
                if(idx == 0):
                    # print current address in the beginning of new line
                    print "%x : " % addr,

                print "%02x" % byte,
                # increment index
                idx += 1
                if(idx == 16):
                    # print new line
                    print ""
                    idx = 0
        except:
            print "Error in printing full filled content"


#===============================================================================
# main script
#===============================================================================
if __name__ == '__main__':
    #parse the command line parameters using OptionParser
    cmd_line_parser = optparse.OptionParser()
    cmd_line_parser.add_option("-f", "--file", action="store", type="string",
            dest="file_name", help="parse TI-TXT file with name FILE",
            metavar="FILE")
    cmd_line_parser.add_option("-v", "--verbose", action="store_true",
            dest="verbose", help="actiate verbose mode")
    cmd_line_parser.add_option("-s", "--start", action="store", type="int",
            dest="start_addr", help="start address with value of SADDR",
            metavar="SADDR")
    cmd_line_parser.add_option("-e", "--end", action="store", type="int",
            dest="end_addr", help="end address with value of EADDR",
            metavar="EADDR")
    (options, args) = cmd_line_parser.parse_args()

    # check given input file name parameter
    if(options.file_name == None):
        print "Input TI-TXT file name is missing!"
        cmd_line_parser.print_help()
        sys.exit(1)

    # create new instance of TI-TXT class
    ti_txt = TiTxtParser(options.file_name, options.verbose)

    # do the parsing
    content = ti_txt.parse()
    if(content == {}):
        print "Failed to parse TI-TXT file:", options.file_name
        sys.exit(1)
    ti_txt.debug_print_content()

    # try to fill the data
    if((options.start_addr != None) and (options.end_addr != None)):
        try:
            full_content = ti_txt.fill(options.start_addr,
                options.end_addr, 0xFF)
            ti_txt.debug_print_full_content(full_content)
        except:
            print "Error on testing filling function"

    # exit
    sys.exit(0)
