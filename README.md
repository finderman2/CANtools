# CANtools
A set of python scripts for easy data logging using the open source CANtact board

**capture.py** Enables the logging of an entire bus or specific ID's with both output to file and terminal logging. It can also output SavvyCAN compatible files. Run -h option for full usage options and flags:

####Examples:
First run <code>capture.py -g</code> to list all available serial ports while the CANtact is unpluged, then again after the device is connected, the new entry should be the board.

To log the whole bus to the terminal at 500kb/s run (note default baudrate is 500kb/s):
<pre><code>capture.py -p /dev/tty.SERIALPORT</code></pre>

To log the whole bus to a file at 125kb/s while filtering for the ID's 0x102 0x3D2 run:
<pre><code>capture.py -b 125000 -p /dev/tty.SERIALPORT -s date -f 0x102 0x3D2</code></pre>
