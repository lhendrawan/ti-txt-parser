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
# Name:        CalcMspGangChksum.py
#
# Description: Simple example python file to use TiTxtParser and calculate
#              the checksum as is used in MSP-GANG
#
# Author:      Leo Hendrawan
#
# Version:     0.3
#
# Licence:     BSD license
#
# Note:        The code for calculating the MSP-GANG checksum is derived from 
#              MSP-GANG User's Guide (SLAU358D)
#
#
# Log:
#     - Version 0.3 (2013.06.29) :
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
# Calculate MSP-GANG Checksum function
#===============================================================================
def CalcMspGangChksum(file_name, verbose):
    # create new instance of TI-TXT class
    ti_txt = TiTxtParser(verbose)

    # parse the TI-TXT
    content = ti_txt.parse(file_name)
    if(content == {}):
        if(verbose == True):
            print "Failed to parse TI-TXT file:", file_name
        return None

    # calculate the checksum
    if(verbose == True):
        print "\n== Calculating MSP-GANG CS =="
    cs = 0
    start_addresses = content.keys()
    start_addresses.sort()
    for start_addr in start_addresses:
        i = 0
        for byte in content[start_addr]:
            if (i == 0):
                cs = cs + byte
                i = 1
            else:
                cs = cs + (byte * 256)
                i = 0
        if(i == 1):
            cs = cs + (0xFF * 256)

    # return the calculated checksum
    return cs


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
            dest="verbose", help="activate verbose mode")
    (options, args) = cmd_line_parser.parse_args()

    # check given input file name parameter
    if(options.file_name == None):
        print ("Input TI-TXT file name is missing!")
        cmd_line_parser.print_help()
        sys.exit(1)

    # calculate checksum
    cs = CalcMspGangChksum(options.file_name, options.verbose)

    # check for valid cs
    if(cs == None):
        print "Fail to calculate checksum!"
        sys.exit(1)
    else:
        print "Calculated MSP-GANG checksum:", hex(cs)

    # exit
    sys.exit(0)
