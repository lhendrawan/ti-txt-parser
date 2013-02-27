@echo off
set INPUT_FILE=test_blink.txt
set INPUT_JOIN_FILE=const.txt
set OUTPUT_FILE=result.txt
set LOG_FILE=log.txt
set DEV_START_ADDR=0xF800
set DEV_END_ADDR=0xFFFF

echo --------------------------------------------------
echo Simple example for parsing TI-TXT file
echo --------------------------------------------------
echo Input file : %INPUT_FILE%
echo Input join file : %INPUT_JOIN_FILE%
echo Output file : %OUTPUT_FILE%
echo Log file : %LOG_FILE%
echo Device flash start address (MSP430G2xx3): %DEV_START_ADDR%
echo Device flash end address (MSP430G2xx3): %DEV_END_ADDR%
echo[
echo The following steps will be executed:
echo - %INPUT_FILE% and %INPUT_JOIN_FILE% are parsed
echo - the result of contents are then joined
echo - the joined content is then filled in continous range from %DEV_START_ADDR% to %DEV_END_ADDR%
echo - final result will be saved into TI-TXT format with the name of %OUTPUT_FILE%
echo[
echo The execution process output log can be found in %LOG_FILE%
python ../../TI-TXT-Parser/TiTxtParser.py -f %INPUT_FILE% -v -o %OUTPUT_FILE% -j %INPUT_JOIN_FILE% -s %DEV_START_ADDR% -e %DEV_END_ADDR% > %LOG_FILE%
echo[
pause