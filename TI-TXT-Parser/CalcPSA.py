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
# Name:        CalcPSA.py
#
# Description: Simple example python file to use TiTxtParser and calculate
#              memory content using PSA method
#
# Author:      Leo Hendrawan
#
# Version:     0.3
#
# Licence:     BSD license
#
# Note:
#
# Log:
#     - Version 0.3 (2013.03.01) :
#       Hello World! (created)
#
#===============================================================================
#!/usr/bin/env python

import sys
import optparse
from TiTxtParser import TiTxtParser


#===============================================================================
# Constants
#===============================================================================

#===============================================================================
# Calculate PSA function
#===============================================================================
def CalcPSA(file_name, start_addr, end_addr, verbose):
    # create new instance of TI-TXT class
    ti_txt = TiTxtParser(verbose)

    # parse the TI-TXT
    content = ti_txt.parse(file_name)
    if(content == {}):
        if(verbose == True):
            print "Failed to parse TI-TXT file:", file_name
        return None

    # try to fill the data
    full_content = ti_txt.fill(content, start_addr, end_addr, 0xFF)
    if(full_content == {}):
        if(verbose == True):
            print "Failed to fill TI-TXT file"
        return None

    # calculate the checksum
    if(verbose == True):
        print "\n== Calculating PSA Checksum =="
    psa_chksum = start_addr - 2
    for byte in full_content[(full_content.keys())[0]]:
        if((psa_chksum & 0x8000) != 0):
            psa_chksum = ((psa_chksum ^ 0x0805) << 1) | 1
        else:
            psa_chksum = psa_chksum << 1
        psa_chksum = (psa_chksum ^ byte) & 0xFFFFFFFF

    # return the calculated checksum
    return psa_chksum


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
    cmd_line_parser.add_option("-s", "--start", action="store", type="int",
            dest="start_addr", help="flash start address with value of SADDR",
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
    elif(options.start_addr == None):
        print "Device flash start address is missing!"
        cmd_line_parser.print_help()
        sys.exit(1)
    elif(options.end_addr == None):
        print "Device flash end address is missing!"
        cmd_line_parser.print_help()
        sys.exit(1)

    # calculate checksum
    checksum = CalcPSA(options.file_name, options.start_addr,
                options.end_addr, options.verbose)

    # check for valid checksum
    if(checksum == None):
        print "Fail to calculate PSA checksum!"
        sys.exit(1)
    else:
        print "Calculated PSA checksum:", hex(checksum)

    # exit
    sys.exit(0)
