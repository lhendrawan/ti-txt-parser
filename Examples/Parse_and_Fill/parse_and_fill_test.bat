@echo off
set INPUT_FILE=test_blink.txt
set OUTPUT_FILE=result.txt
set LOG_FILE=log.txt
set DEV_START_ADDR=0x5C00
set DEV_END_ADDR=0x10100

echo --------------------------------------------------
echo Simple example for filling TI-TXT files
echo --------------------------------------------------
echo Input file : %INPUT_FILE%
echo Output file : %OUTPUT_FILE%
echo Log file : %LOG_FILE%
echo[
echo The following steps will be executed:
echo - %INPUT_FILE% is parsed
echo - the parsed contents is then filled with empty bytes (0xFF) between %DEV_START_ADDR% and %DEV_END_ADDR%
echo - the final result will be saved into TI-TXT format with the name of %OUTPUT_FILE%
echo[
echo The execution process output log can be found in %LOG_FILE%
python ..\..\Scripts\TiTxtParser.py -f %INPUT_FILE% -v -o %OUTPUT_FILE% -s %DEV_START_ADDR% -e %DEV_END_ADDR% > %LOG_FILE%
echo[
pause