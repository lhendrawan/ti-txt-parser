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
# Name:        GenUniqueId.py
#
# Description: Simple example python file to use TiTxtParser generating multiple
#              output files from one input TI-TXT file with different (unique)
#              ID in each output file
#
# Author:      Leo Hendrawan
#
# Version:     0.3
#
# Licence:     BSD license
#
# Note:        The script will modify the last byte of six bytes ID number 
#              located starting address 0x1000
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
# Generate Output files with unique ID
#===============================================================================
def GenUniqueId(in_file, out_file, num_of_output, verbose):
    # create new instance of TI-TXT class
    ti_txt = TiTxtParser(verbose)

    # parse the TI-TXT
    content = ti_txt.parse(in_file)
    if(content == {}):
        if(verbose == True):
            print "Failed to parse TI-TXT file:", in_file
        return None

    # check if the ID fields is available
    try:
        if((len(content[0x1000]) == 6) and (verbose == True)):
            print "6 bytes Unique ID starting at address 0x1000 is found"
    except:
        if(verbose == True):
            print "No Unique ID starting at address 0x1000 is found"
            return False
    
    
    # start creating files
    if(verbose == True):
        print "\n== Generating output file with Unique ID =="
    for i in range(0, num_of_output):
      file_name = out_file.split('.')[0] + "-" + str(i) + "." + out_file.split('.')[1]
      temp = content
      temp[0x1000][5] = i
      if(verbose == True):
          id = temp[0x1000]
          id_string = hex(id[0]) + ":" + hex(id[1]) + ":" + hex(id[2]) + ":" + \
              hex(id[3]) + ":" + hex(id[4]) + ":" + hex(id[5])
          print "\nOutput file name: ", file_name, " - ID: ", id_string
      ti_txt.print_ti_txt(file_name, temp)
      
    return True


#===============================================================================
# main script
#===============================================================================
if __name__ == '__main__':
    #parse the command line parameters using OptionParser
    cmd_line_parser = optparse.OptionParser()
    cmd_line_parser.add_option("-f", "--file", action="store", type="string",
            dest="in_file_name", help="TI-TXT input file with name IN_FILE",
            metavar="IN_FILE")
    cmd_line_parser.add_option("-o", "--out", action="store", type="string",
            dest="out_file_name", help="TI-TXT output file with name OUT_FILE",
            metavar="OUT_FILE")
    cmd_line_parser.add_option("-v", "--verbose", action="store_true",
            dest="verbose", help="activate verbose mode")
    cmd_line_parser.add_option("-n", "--num", action="store", type="int",
            dest="num_output", help="number of output files",
            metavar="NUM_OUTPUT")
    (options, args) = cmd_line_parser.parse_args()

    # check given input file name parameter
    if(options.in_file_name == None):
        print ("Input TI-TXT file name is missing!")
        cmd_line_parser.print_help()
        sys.exit(1)
    if(options.out_file_name == None):
        print ("Output TI-TXT file name is missing!")
        cmd_line_parser.print_help()
        sys.exit(1)
    elif(options.num_output == None):
        print ("Number of output file is missing!")
        cmd_line_parser.print_help()
        sys.exit(1)

    # calculate checksum
    ret = GenUniqueId(options.in_file_name, options.out_file_name,
                      options.num_output, options.verbose)

    # check for valid cs
    if(ret != True):
        print "\nFail to generate output file!"
        sys.exit(1)
    else:
        print "\n ", options.num_output, " Output files successfully generated"
        
    # exit
    sys.exit(0)
