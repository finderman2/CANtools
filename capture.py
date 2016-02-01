"""

Title: CANtact Capture
Desc: Enables the logging of an entire bus or specific ID's with both output to file and terminal logging. It can also output SavvyCAN compatible files.
Version: 0.4
Release Notes: 
Authors: Jean-Claude Thibault, Liam O'Brien

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
For a full copy of the license please vist this website: http://creativecommons.org/licenses/by-nc-sa/4.0/

"""
from __future__ import print_function

#Functions
def getSerialPorts():
    """Lists serial ports

    :raises EnvironmentError:
        On unsupported or unknown platforms
    :returns:
        A list of available serial ports
    """
    if sys.platform.startswith('win'):
        ports = ['COM' + str(i + 1) for i in range(256)]

    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this is to exclude your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')

    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')

    else:
        raise EnvironmentError('Unsupported platform')
    
    print("Available Serial Ports:")
    
    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def ishex(value):
    if value[:2] == "0x":
        return True
    else:
        print("Filter ID is not in hex format")
        return False

def process_args(args):
    parser = argparse.ArgumentParser(
        description="Enables the logging of an entire bus or specific ID's with both output to file and terminal logging. It can also output SavvyCAN compatible files."
    )
    
    parser.add_argument('-b', '--baudrate', dest='baudrate', type=int, default=500000, help='CAN Bus Baudrate')
    parser.add_argument('-p', '--port', dest='port', type=str, default='/dev/tty.usbmodem1421', help='CAN Bus Serial Port')
    parser.add_argument('-w', '--write', dest='write', type=str, default='', help='Save data to a file, passing the option "date" saves the file with a filename of yyyy/mm/dd hh:mm:ss, any other option becomes the filename')
    parser.add_argument('-l', '--log', dest='log', action='store_false', default=True, help='Enabled by default, log data to the terminal window')
    parser.add_argument('-c', '--frame-count', dest='frame-count', type=int, default=10000, help='Number of frames to capture before terminating')
    parser.add_argument('-f', '--filter', dest='filter', nargs='+', help='Filter the output to only the ID\'s in your filter (eg -f 0x102 0x3D2)')
    parser.add_argument('-s', '--savvy', dest='savvy', action='store_true', default=False, help='Enable loging in a SavvyCAN compatible format')
    parser.add_argument('-g', '--get-device', dest='getD', action='store_true', default=False, help='Output list of connected serial devices')
    
    options = parser.parse_args(args)
    return vars(options)

#Main Import
import sys
import glob
import time, datetime
import io
import argparse

#Windows specific modules
if sys.platform.startswith('win'):
    import msvcrt
    from msvcrt import getch    

#import CANard + Serial
from canard import can
from canard.hw import cantact
import serial

#User Configuration ------------------

#CAN Settings
CAN_BAUDRATE = 500000
MAX_NUMBER_OF_FRAMES = 0
SERIAL_PORT = '/dev/cu.usbmodem1421'
ID_FILTER = ['0x266'] #ID must be specified with 0x prefix

#Logging/Viewing Settings
SHOW_ALL_IDs = True #True displays all ID's, False using the ID_FILTER to only display the selected ID's
WRITE_TO_FILE = False
SHOW_POWER_DATA = False
LOGGING_ENABLED = True
FILE_NAME = '' #Defaults to current date and time

#SavvyCAN Related Settings
SAVVYCAN_FORMAT_ENABLE = False
SAVVYCAN_BUS = '0'

#System Setup
SEC_BETWEEN_CAPTURE = 0
ONLINE = True

#get arguments from the CLI
opt = process_args(sys.argv[1:])

#Global Variables
frame_counter = 0

#Parse CLI arguments
LOGGING_ENABLED = opt['log'] #logging to the terminal is enabled by default
MAX_NUMBER_OF_FRAMES = opt['frame-count'] #max number of frames is 10000 by default

if opt['baudrate'] >= 125000 and opt['baudrate'] <= 1000000:
    CAN_BAUDRATE = opt['baudrate']
else:
    raise argparse.ArgumentTypeError('CAN baudrate must be between 125kb/s and 1mb/s')

if opt['port'] != '':
    SERIAL_PORT = opt['port']
else:
    raise argparse.ArgumentTypeError('Must set a serial port, eg COM8 or /dev/tty.*')

if opt['write'] == 'date':
    WRITE_TO_FILE = True
elif opt['write'] != '':
    WRITE_TO_FILE = True
    FILE_NAME = opt['write']

if opt['filter'] != []:
    SHOW_ALL_IDs = False
    ID_FILTER = opt['filter']

if opt['savvy'] == True:
    SAVVYCAN_FORMAT_ENABLE = True
    print("SavvyCAN Format Enabled")

if opt['getD'] == True:
    print(getSerialPorts())
    exit()

#Begin the main program -------------------
if ONLINE == True:
  #Setup CANtact Interface
  dev = cantact.CantactDev(SERIAL_PORT)
  dev.set_bitrate(CAN_BAUDRATE) 
  #Connect to the Device
  dev.start()
  print("CANtact running on " + SERIAL_PORT + " at " + str(CAN_BAUDRATE) + "kb/s...")
  
if WRITE_TO_FILE == True:
  if FILE_NAME != '':
      st = FILE_NAME
  else:
      st = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H.%M.%S')
       
  file_ = open(st + '.txt', 'w')
  print('New File Opened, now logging data')

#Run through the capture loop until the maximum number of frames is reached
while frame_counter <= MAX_NUMBER_OF_FRAMES:
  message = dev.recv()
  
  # Parse the id, create a frame
  #frame_id = int(message.id, 16)
  frame_id = message.id
  frame_id_hex = hex(message.id)
  
  # Filtering
  if (frame_id_hex in ID_FILTER) or (SHOW_ALL_IDs == True and frame_id_hex!='e'):
    
    frame = can.Frame(frame_id)
    frame_counter = frame_counter + 1
  
    # Set our frame equal to message data
    frame.dlc = message.dlc
    frame.data = message.data
    
    #bytesHex = []
    #for data in message.data:
        #for each data byte in our frame convert it to hex and add it to a list minus the 0x part
        #bytesHex.append(hex(data)[2:])
        
    #print(bytesHex)
        
    #Make the frame string
    data_for_file = ("%s" % (frame.data))
    console_data = (" %s, %s, %s, %s\n" % (time.time(), hex(frame.id)[2:], frame.dlc, data_for_file[1:len(data_for_file)-1]))
    #Remove spaces between commas
    data_for_file = data_for_file.replace(" ", "")
    
    #Log frame to console if enabled
    if WRITE_TO_FILE == True:
        #Format the data for writing to file
        if SAVVYCAN_FORMAT_ENABLE == True:
            write_data = ("%s,%s,%s,%s,%s,%s\n" % (time.time(), hex(frame.id)[2:], frame.is_extended_id, SAVVYCAN_BUS, frame.dlc, data_for_file[1:len(data_for_file)-1]))
        else:
            #Write data in format to be used with CANDecoder
            #fixed bug that would cause the first digit of data to be deleted
            write_data = ("%s,%s,%s,%s\n" % (time.time(), hex(frame.id)[2:], frame.dlc, data_for_file[1:len(data_for_file)-1]))
        
        #Write Formated data to file
        file_.write(write_data)
        #display how many frames we have saved so far
        print(frame_counter)
        
    elif LOGGING_ENABLED == True:
        #Log data to console instead
        print(console_data)
    
    if SEC_BETWEEN_CAPTURE > 0:
      time.sleep(SEC_BETWEEN_CAPTURE)      
      print('Out of while loop')

if WRITE_TO_FILE == True:
  file_.close()
  print("File " + st + '.txt closed.')

#After file is written set online to false to exit program
ONLINE = False

if ONLINE == False:
  dev.stop()
  print("CANtact Connection Closed")