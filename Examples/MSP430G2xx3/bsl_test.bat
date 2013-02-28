@echo off
set INPUT_FILE=test_blink.txt
set COM_PORT=COM68
set DEV_START_ADDR=0xF800

echo %PYTHONPATH%

echo ----------------------------------------------------------
echo Simple example for flashing TI-TXT file to MSP430G2xx BSL
echo ----------------------------------------------------------
echo Input file : %INPUT_FILE%
echo COM PORT: %COM_PORT%
echo Device flash start address (MSP430G2xx3): %DEV_START_ADDR%
echo[
echo !!Make sure that target device enters BSL mode!!
pause
python ../../TI-TXT-Parser/MSP430G2xxBslScripter.py -f %INPUT_FILE% -v -s %DEV_START_ADDR% -p %COM_PORT%
echo[
pause