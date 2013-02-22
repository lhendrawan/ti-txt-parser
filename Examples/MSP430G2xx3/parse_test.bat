@echo off
set INPUT_FILE=test_blink.txt
set OUTPUT_FILE=parse_result.txt
set DEV_START_ADDR=0xF800
set DEV_END_ADDR=0xFFFF

echo --------------------------------------------------
echo Simple example for parsing TI-TXT file
echo --------------------------------------------------
echo Input file : %INPUT_FILE%
echo Output file : %OUTPUT_FILE%
echo Device flash start address (MSP430G2xx3): %DEV_START_ADDR%
echo Device flash end address (MSP430G2xx3): %DEV_END_ADDR%

python ../../TI-TXT-Parser/TiTxtParser.py -f %INPUT_FILE% -v -s %DEV_START_ADDR% -e %DEV_END_ADDR% > %OUTPUT_FILE%
pause