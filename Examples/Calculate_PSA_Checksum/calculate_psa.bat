@echo off
set INPUT_FILE=input.txt
set LOG_FILE=log.txt
set DEV_START_ADDR=0x5C00
set DEV_END_ADDR=0x10100

echo --------------------------------------------------------------
echo Simple example for calculating PSA checksum of TI-TXT files
echo --------------------------------------------------------------
echo Input file : %INPUT_FILE%
echo Log file : %LOG_FILE%
echo[
echo The following steps will be executed:
echo - %INPUT_FILE% is parsed
echo - the parsed contents is then filled with empty bytes (0xFF) between %DEV_START_ADDR% and %DEV_END_ADDR%
echo - the PSA checksum value of filled contents is then calculated
echo[
echo The execution process output log can be found in %LOG_FILE%
python ..\..\TI-TXT-Parser\CalcPSA.py -f %INPUT_FILE% -v -s %DEV_START_ADDR% -e %DEV_END_ADDR% > %LOG_FILE%
echo[
pause