/******************************************************************************
* README.txt 
*
* TI-TXT-Parser - Python Script file for parsing TI-TXT file format
*
* version : 0.3
*
******************************************************************************/

TI-TXT-Parser is an open source script written in Python programming language
for parsing TI-TXT file format. 

The parser can be used for example to generating TI-TXT file format in full
(filled) format. One useful example is to use the parser to communicate
with the MSP430G2xx BSL which is described in SLAA450 application note
(http://www.ti.com/lit/pdf/slaa450).


/******************************************************************************
* Documentation
******************************************************************************/

TODO

/******************************************************************************
* Directory Structures 
******************************************************************************/

<ROOT_DIRECTORY>
  |
  |- Examples : project code and examples
  |   |
  |   |- Calculate_MSPGANG_CS: script file example for calculating checksum 
  |   |                        which is used by MSP-GANG
  |   |
  |   |- Generate_Unique_ID: script file example for generating multiple output
  |   |                      files with unique ID from a single input file
  |   |
  |   |- MSP430G2xx3_BSL: script file example for using MSP430G2xxBslHost 
  |   |                   python code with the MSP430G2xx3 MCU family on 
  |   |                   MSP-EXP430G2 Launchpad development board
  |   |
  |   |- Parse_and_Fill : script file example for using TiTxtParser to 
  |   |                   parse and fill TI-TXT files
  |   |
  |   |- Parse_and_Join : script file example for using TiTxtParser to
  |                       join two TI-TXT input files
  |    
  |- Scripts: source code of TI-TXT-Parser and example scripts
