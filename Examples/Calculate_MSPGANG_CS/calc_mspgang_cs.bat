@echo off
set INPUT_FILE=input.txt
set LOG_FILE=log.txt

echo --------------------------------------------------------------------
echo Simple example for calculating MSP-GANG checksum of TI-TXT files
echo --------------------------------------------------------------------
echo Input file : %INPUT_FILE%
echo Log file : %LOG_FILE%
echo[
echo The following steps will be executed:
echo - %INPUT_FILE% is parsed
echo - the checksum value used in MSP-GANG is then calculated
echo[
echo The execution process output log can be found in %LOG_FILE%
python ..\..\TI-TXT-Parser\CalcMspGangChksum.py -f %INPUT_FILE% -v > %LOG_FILE%
echo[
pause