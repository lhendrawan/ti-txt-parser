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
# Version:     0.3
#
# Licence:     New BSD license
#
# Note:
#
# Log:
#     - Version 0.1 (2013.02.22) :
#       Hello World! (created)
#     - Version 0.2 (2013.02.28):
#        * removing class variables file_name and content to make TiTxtParser
#          class more flexible (e.g. for join() method)
#        * removing debug_print_full_content method
#        * adding join() method
#     - Version 0.3 (2013.06.29):
#        * bug fix in the print_ti_txt() and fill() method
#        * some typo bug fixes
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
    # flag for verbose mode
    verbose_mode = False

    #---------------------------------------------------------------------------
    # Class functions
    #---------------------------------------------------------------------------

    #---------------------------------------------------------------------------
    # init function - instantiation operation
    #---------------------------------------------------------------------------
    def __init__(self, verbose=False):
        # save file name and verbose mode
        self.verbose_mode = verbose

    #---------------------------------------------------------------------------
    # setting verbose mode
    #---------------------------------------------------------------------------
    def set_verbose_mode(self, verbose):
        self.verbose_mode = verbose

    #---------------------------------------------------------------------------
    # get list of addresses in TI-TXT file content
    #---------------------------------------------------------------------------
    def get_addr_list(self, content):
        # create empty list
        addr_list = []

        # get and sort the start addresses
        start_addresses = content.keys()
        start_addresses.sort()

        # append each address
        for start_addr in start_addresses:
            idx = 0
            for bytes in content[start_addr]:
                addr_list.append(start_addr + idx)
                idx += 1

        return addr_list

    #---------------------------------------------------------------------------
    # get start address in TI-TXT file content
    #---------------------------------------------------------------------------
    def get_start_addr(self, content):
        start_addr = -1
        try:
            for addr in content.keys():
                if(start_addr == -1):
                    # first iteration
                    start_addr = addr
                else:
                    if(addr < start_addr):
                        # save new start address
                        start_addr = addr
        except:
            pass
        return start_addr

    #---------------------------------------------------------------------------
    # get end address in TI-TXT file content
    #---------------------------------------------------------------------------
    def get_end_addr(self, content):
        end_addr = -1
        try:
            for addr in content.keys():
                if(end_addr == -1):
                    # first iteration
                    end_addr = addr
                else:
                    if(addr > end_addr):
                        # save new end address
                        end_addr = addr

            # add the length
            if(end_addr != -1):
                end_addr += len(content[end_addr]) - 1
        except:
            pass
        return end_addr

    #---------------------------------------------------------------------------
    # parse the TI-TXT file
    #---------------------------------------------------------------------------
    def parse(self,file_name):
        if(self.verbose_mode == True):
            print "\n== Parsing TI-TXT File:", file_name, " =="

        # try to open input file
        try:
            if(self.verbose_mode == True):
                print "Opening TI-TXT File: ", file_name
            file = open(file_name, 'r')
        except:
            if(self.verbose_mode == True):
                print "Error in opening TI-TXT file ", file_name
            return {}

        # start parsing
        content = {}
        for line in file:
            # check if this is a start address line
            if(line.find('@') != -1):
                try:
                    # add new entry in dictinary
                    addr_num = line.lstrip('@')
                    start_addr = int(addr_num,16)
                    content[start_addr] = []
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
                            content[start_addr].append(byte_int)
                    except:
                        if(self.verbose_mode == True):
                            print "Error while trying to convert: ", byte_str
                        file.close()
                        return {}

        # close file
        file.close()

        # return content as dictionary
        return content

    #---------------------------------------------------------------------------
    # fill the empty memory of TI-TXT file content
    #---------------------------------------------------------------------------
    def fill(self, content, start_addr, end_addr, fill_byte):
        if(self.verbose_mode == True):
            print "\n== Filling memory range =="

        # initialize variable
        full_content = {}

        # check for starting and ending address
        if(start_addr > self.get_start_addr(content)):
            if(self.verbose_mode == True):
                print "Invalid Start Address: ", hex(start_addr),
                print " - TI-TXT content start address: ", self.get_start_addr()
            return {}
        elif(end_addr < self.get_end_addr(content)):
            if(self.verbose_mode == True):
                print "Invalid End Address: ", hex(end_addr),
                print " - TI-TXT content end address: ", self.get_end_addr()
            return {}

        # print start message
        if(self.verbose_mode == True):
            print "Start Addr:", hex(start_addr)
            print "End Addr:", hex(end_addr)
            print "Fill byte:", hex(fill_byte)

        # now we can work - make a list of key addresses of the TI-TXT
        # original content
        addr_keys = content.keys()
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
                print "Copying ", len(content[addr]),
                print "bytes data from address ", hex(addr)
            full_content[start_addr] = full_content[start_addr] + content[addr]
            # update start address
            addr_idx += len(content[addr])

        # fill the end if necessary
        if(addr_idx < end_addr):
            if(self.verbose_mode == True):
                print "Filling empty byte(s) from address", hex(addr_idx),
                print "to address ", hex(end_addr)
            loop = range(addr_idx, end_addr)
            for i in loop:
                full_content[start_addr].append(fill_byte)
                addr_idx += 1

        # return
        return full_content

    #---------------------------------------------------------------------------
    # join two TI-TXT file contents
    #---------------------------------------------------------------------------
    def join(self, content1, content2):
        if(self.verbose_mode == True):
            print "\n== Joining two TI-TXT contents =="
        # get list of address of both contents
        list1 = self.get_addr_list(content1)
        list2 = self.get_addr_list(content2)
        #check if there are overlapping address
        overlap = False
        for addr in list1:
            try:
                overlap_addr = list2.index(addr)
                overlap = True
                if(self.verbose_mode == True):
                    print "Overlapping address:", hex(addr)
            except:
                pass

        # abort if overlapping address found
        if(overlap == True):
            return {}

        # append content2 to content1
        if(self.verbose_mode == True):
            print "No overlapping address found, appending contents"
        res_content = content1
        for addr in content2.keys():
            res_content[addr] = content2[addr]

        # append content2 to content 1
        return (res_content)


    #---------------------------------------------------------------------------
    # print content into TI-TXT file format
    #---------------------------------------------------------------------------
    def print_ti_txt(self, file_name, content):
        if(self.verbose_mode == True):
            print "\n== Print out TI-TXT file:", file_name, "=="

        # check for content data type (must be dictionary):
        if(type(content) != dict):
            if(self.verbose_mode == True):
                print "Invalid input content data type:", type(content)
            return False

        # try to open file
        try:
            if(self.verbose_mode == True):
                print "Opening file in write mode"
            file = open(file_name, 'w')
        except:
            if(self.verbose_mode == True):
                print "Failed to open file in write mode"
            return False

        # sort the content address
        addr_sorted = content.keys()
        addr_sorted.sort()

        # start writing file
        for addr in addr_sorted:
            # write starting address
            if(self.verbose_mode == True):
                print "Writing memory starting from address ", hex(addr)
            line = "@" + hex(addr).lstrip("0x") + "\n"
            file.write(line);

            # write bytes, maximum 16 bytes per line
            idx = 0
            line = ""
            for byte in content[addr]:
                line += "%02x" % byte + " "
                idx += 1
                if(idx == 16):
                    # write line to file
                    line += "\n"
                    file.write(line)
                    # prepare new line
                    line = ""
                    idx = 0

            # flush data
            if(idx != 0):
                line += "\n"
                file.write(line)

        #print end of file
        file.write("q\n")

        #close file
        file.close()
        if(self.verbose_mode == True):
            print "Finished writing TI-TXT file"
        return True


    #---------------------------------------------------------------------------
    # Debug print TI-TXT file content
    #---------------------------------------------------------------------------
    def debug_print_content(self, content):
        try:
            print "\n== Print out TI-TXT content =="
            start_addresses = content.keys()
            start_addresses.sort()
            for start_addr in start_addresses:
                # calculate end address
                end_addr = start_addr + len(content[start_addr]) - 1
                addr_range = range (start_addr, end_addr+1)
                bytes = content[start_addr]
                idx = 0
                for addr in addr_range:
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
                print ""
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
            dest="verbose", help="activate verbose mode")
    cmd_line_parser.add_option("-s", "--start", action="store", type="int",
            dest="start_addr", help="start address with value of SADDR",
            metavar="SADDR")
    cmd_line_parser.add_option("-e", "--end", action="store", type="int",
            dest="end_addr", help="end address with value of EADDR",
            metavar="EADDR")
    cmd_line_parser.add_option("-j", "--join", action="store", type="string",
            dest="join_file_name",
            help="join main TI-TXT file with second file with name JOINFILE",
            metavar="JOINFILE")
    cmd_line_parser.add_option("-o", "--output", action="store", type="string",
            dest="out_file_name", help="output TI-TXT file with name OUTFILE",
            metavar="OUTFILE")
    (options, args) = cmd_line_parser.parse_args()

    # check given input file name parameter
    if(options.file_name == None):
        print "Input TI-TXT file name is missing!"
        cmd_line_parser.print_help()
        sys.exit(1)

    # create new instance of TI-TXT class
    ti_txt = TiTxtParser(options.verbose)

    # do the parsing
    content = ti_txt.parse(options.file_name)
    if(content == {}):
        print "Failed to parse TI-TXT file:", options.file_name
        sys.exit(1)
    if(options.verbose == True):
        ti_txt.debug_print_content(content)

    # check if there is secondary input file to be joined
    if(options.join_file_name != None):
        content2 = ti_txt.parse(options.join_file_name)
        if(options.verbose == True):
            ti_txt.debug_print_content(content2)
        try:
            content = ti_txt.join(content, content2)
        except:
            print "Error on joining contents"
            sys.exit(1)
        if(content == {}):
            print "Error on joining contents"
            sys.exit(1)

    # try to fill the data
    if((options.start_addr != None) and (options.end_addr != None)):
        try:
            full_content = ti_txt.fill(content, options.start_addr,
                options.end_addr, 0xFF)
        except:
            print "Error on testing filling function"
            sys.exit(1)
    else:
        full_content = content

    # print filled data to a TI-TXT format file
    if(options.out_file_name != None):
        if(options.verbose == True):
            ti_txt.debug_print_content(full_content)
        res = ti_txt.print_ti_txt(options.out_file_name, full_content)
        if (res != True):
            print "Failed to write output filled TI-TXT file!"
            sys.exit(1)

    # exit
    sys.exit(0)
