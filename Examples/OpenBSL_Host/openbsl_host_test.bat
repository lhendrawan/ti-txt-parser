@echo off
set INPUT_FILE1=Timer_A0.txt
set INPUT_FILE2=Timer_A1.txt
set COM_PORT=COM6

echo --------------------------------------------------------------------
echo Simple example for flashing TI-TXT file with OpenBSL on MSP430G2553
echo --------------------------------------------------------------------
echo Input file 1 : %INPUT_FILE1%
echo Input file 2 : %INPUT_FILE2%
echo COM PORT: %COM_PORT%
echo[
echo Flashing %INPUT_FILE1% - blinking LED1 (green LED) with Timer_A0 interrupt
echo Reset device and make sure that OpenBSL is running on the device!!
pause
python ..\..\Scripts\OpenBSLHost.py -i %INPUT_FILE1% -v -p %COM_PORT%
echo[
echo Flashing %INPUT_FILE2% - blinking LED2 (red LED) with Timer_A1 interrupt
echo Reset device and make sure that OpenBSL is running on the device!!
pause
python ..\..\Scripts\OpenBSLHost.py -i %INPUT_FILE2% -v -p %COM_PORT%
echo[
pause