@echo off
set INPUT_FILE1=test_blink1.txt
set INPUT_FILE2=test_blink2.txt
set COM_PORT=COM84
set DEV_START_ADDR=0xF800

echo ----------------------------------------------------------
echo Simple example for flashing TI-TXT file to MSP430G2xx BSL
echo ----------------------------------------------------------
echo Input file 1 : %INPUT_FILE1%
echo Input file 2 : %INPUT_FILE2%
echo COM PORT: %COM_PORT%
echo Device flash start address (MSP430G2xx3): %DEV_START_ADDR%
echo[
echo Flashing %INPUT_FILE1%
echo Reset device and make sure that target device enters BSL mode!!
pause
python ..\..\Scripts\MSP430G2xxBslHost.py -f %INPUT_FILE1% -v -s %DEV_START_ADDR% -p %COM_PORT%
echo[
echo Flashing %INPUT_FILE2%
echo Reset device and make sure that target device enters BSL mode!!
pause
python ..\..\Scripts\MSP430G2xxBslHost.py -f %INPUT_FILE2% -v -s %DEV_START_ADDR% -p %COM_PORT%
echo[
pause