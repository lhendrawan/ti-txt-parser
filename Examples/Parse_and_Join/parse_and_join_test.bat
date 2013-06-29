@echo off
set INPUT_FILE=test_blink.txt
set INPUT_JOIN_FILE=const.txt
set OUTPUT_FILE=result.txt
set LOG_FILE=log.txt

echo --------------------------------------------------
echo Simple example for joining TI-TXT files
echo --------------------------------------------------
echo Input file : %INPUT_FILE%
echo Input join file : %INPUT_JOIN_FILE%
echo Output file : %OUTPUT_FILE%
echo Log file : %LOG_FILE%
echo[
echo The following steps will be executed:
echo - %INPUT_FILE% and %INPUT_JOIN_FILE% are parsed
echo - the contents of both files are then joined
echo - the final result will be saved into TI-TXT format with the name of %OUTPUT_FILE%
echo[
echo The execution process output log can be found in %LOG_FILE%
python ..\..\Scripts\TiTxtParser.py -f %INPUT_FILE% -v -o %OUTPUT_FILE% -j %INPUT_JOIN_FILE% > %LOG_FILE%
echo[
pause