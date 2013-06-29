@echo off
set INPUT_FILE=input.txt
set LOG_FILE=log.txt
set NUM_OUT=10
set OUT_FILE=output.txt

echo --------------------------------------------------------------------
echo Simple example for generating output TI-TXT files with unique ID
echo --------------------------------------------------------------------
echo Input file : %INPUT_FILE%
echo Output file : %OUT_FILE%
echo Number of Output files: %NUM_OUT%
echo Log file : %LOG_FILE%
echo[
echo The following steps will be executed:
echo - %INPUT_FILE% is parsed
echo - The 6 bytes unique ID at address 0x1000 will be checked
echo - generating output file with last byte of the unique ID incremented
echo[
echo The execution process output log can be found in %LOG_FILE%
echo python ..\..\TI-TXT-Parser\GenUniqueId.py -f %INPUT_FILE% -o %OUT_FILE% -n %NUM_OUT% -v > %LOG_FILE%
python ..\..\TI-TXT-Parser\GenUniqueId.py -f %INPUT_FILE% -o %OUT_FILE% -n %NUM_OUT% -v > %LOG_FILE%
echo[
pause