"""

Title: CANtact Capture
Desc: Enables the logging of an entire bus or specific ID's with both output to file and terminal logging. It can also output SavvyCAN compatible files.
Version: 0.21
Release Notes: 
Authors: Jean-Claude Thibault, Liam O'Brien

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
For a full copy of the license please vist this website: http://creativecommons.org/licenses/by-nc-sa/4.0/

"""

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




#Main Import
import sys
import glob
import time, datetime
import io

#Windows specific modules
if sys.platform.startswith('win'):
    import msvcrt
    from msvcrt import getch
else:
    print("Skipping msvcrt import not running windows")

#import CANard + Serial
from canard import can
from canard.hw import cantact
import serial

#User Configuration
SERIAL_PORT = '/dev/cu.usbmodem1421'
CAN_BAUDRATE = 500000
MAX_NUMBER_OF_FRAMES = 10000
SHOW_ALL_IDs = False #True displays all ID's, False using the frame_id_filter to only display the selected ID's
WRITE_TO_FILE = False
FILE_NAME = 'BusCharging' #Defaults to current date and time
LOGGING_ENABLED = True
frame_id_filter = ['0x254'] #ID must be specified with 0x prefix
#frame_id_filter = ['0x20a', '0x21a', '0x22a', '0x23a', '0x24a', '0x25a', '0x26a', '0x27a', '0x30', '0x31a', '0x32', '0x33a', '0x34a', '0x35a', '0x36a', '0x37a', '0x39a', '0x3aa', '0x3ba', '0x3ca', '0x3ea', '0x48a', '0x49a', '0x4aa', '0x4ba', '0x64a', '0x65a', '0x66a', '0x74a'] #thermal controller id's

#SavvyCAN Settings
SAVVYCAN_FORMAT_ENABLE = False
SAVVYCAN_BUS = '0'

#System Setup
SEC_BETWEEN_CAPTURE = 0
ONLINE = True

#Global Variables
frame_counter = 0

#Prints a list of available serial ports everytime the application is started
#Can be commented out once you know which port your device is on
#print(getSerialPorts())

if ONLINE == True:
  #Setup CANtact Interface
  dev = cantact.CantactDev(SERIAL_PORT)
  dev.set_bitrate(CAN_BAUDRATE)
  #Connect to the Device
  dev.start()
  print("CANtact running on " + SERIAL_PORT + "...")
  
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
  if (frame_id_hex in frame_id_filter) or (SHOW_ALL_IDs == True and frame_id_hex!='e'):
    
    frame = can.Frame(frame_id)
    frame_counter = frame_counter + 1
  
    # Set our frame equal to message data
    frame.dlc = message.dlc
    frame.data = message.data
    
    #print(frame.data)
    
    #print(message.data)
    
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
    else:
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
  
