# Running OpenBSL Host Demo on Windows PC #

The release of TI-TXT-Parser includes a host demo for open source light-weight bootstrap loader for MSP430G2553 target device running MSP-EXP430G2 Launchpad. Below is the step-by-step guide to run the demo.

## Installing Python on the Windows PC ##
  * Download Python installer v2.x (at the moment of writing - v2.7.5) from python.org [here](http://www.python.org/download/). Select the correct processor platform of the Windows PC (32 bit/64 bit). Make sure that the path to Python binaries is added into the PATH environment variables (e.g. refer to [this guide](http://docs.python-guide.org/en/latest/starting/install/win/))
  * Download and install pyserial from the following [link](https://pypi.python.org/pypi/pyserial). For 64 bit machine, download the .tar.gz package and install it manually as described in the [installation guide](http://pyserial.sourceforge.net/pyserial.html#installation).


## Preparing the Hardware ##
  * Insert MSP430G2553 DIP package on the MSP-EXP430G2 Launchpad board and make sure that the UART backchannel jumpers are correctly set as shown [here](http://processors.wiki.ti.com/index.php/File:Msp430g2xx_bsl_uart_conn.PNG).


## Compiling the OpenBSL Code ##
  * Download and extract the OpenBSL\_v0.1.zip file from the [download page](https://code.google.com/p/ti-txt-parser/downloads/list).
  * Import the project which can found under OPEN\_BSL\_EXTRACT\_FOLDER\OpenBSL\projects\MSP430G2553\CCS using CCS v5.5. Make sure to **uncheck** the "Copy projects into workspace" option when importing the project.
  * Connect the Launchpad to the PC, then compile and download the code into target device MSP430G2553. Run the binary, and end the debug session, push RESET button on the Launchpad.


## Running the OpenBSL Host Demo ##
  * Download and extract the ti-txt-parser\_v0.3.zip file from the [download page](https://code.google.com/p/ti-txt-parser/downloads/list).
  * Open the openbsl\_host\_test.bat file which can be found under TI-TXT-PARSER\_EXTRACT\_FOLDER\ti-txt-parser\Examples\OpenBSL\_Host using text editor (e.g. Notepad), and change the COM\_PORT setting to the COM PORT name assigned by Windows OS to the Launchpad UART port (Check it with Windows Device Manager for "MSP430 Application UART" as described [here](http://processors.wiki.ti.com/index.php/EZ430_Backchannel_UART_Configuration)). Save the file after changing the COM\_PORT setting.
  * Click the openbsl\_host\_test.bat, it will first ask to make sure that the device is running OpenBSL code. After pressing any key to continue, it will download a input binary (TIMER\_A0.txt) which will make the MSP430G2553 toggling the LED1 (red LED) on the MSP-EXP430G2 Launchpad kit using TIMER\_A0 CCR0 interrupt. For reference, the application source code for the binary can be found under OPEN\_BSL\_EXTRACT\_FOLDER\OpenBSL\app\_examples\OpenBSL\_AppExample\_MSP430G2553\_CCS directory.
  * Then the batch file will ask to reset the device, and press any key to download the other input binary (TIMER\_A1.txt) which will make MSP430G2553 toggling the LED2 (green LED) on the MSP-EXP430G2 Launchpad kit using TIMER\_A1 CCR0 interrupt.