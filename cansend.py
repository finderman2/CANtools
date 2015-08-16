"""

Title: CANtact Send
Desc: Allows you to send saved CAN data out to the bus
Version: 0.1
Release Notes:
Authors: Liam O'Brien

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
For a full copy of the license please vist this website: http://creativecommons.org/licenses/by-nc-sa/4.0/

"""

from canard import can
from canard.hw import cantact
import sys


#Serial Configuration
SERIAL_PORT = '/dev/cu.usbmodem1421'
CAN_BAUDRATE = 500000

#Setup CANtact Interface
dev = cantact.CantactDev(SERIAL_PORT)
dev.set_bitrate(CAN_BAUDRATE)
print("CANtact running on " + SERIAL_PORT + "...")

#Get file name from user and save to variable
if sys.version_info[0] > 2:
    fileName = input("Please Enter a file Name: ")
else:
    fileName = raw_input("Please Enter a file Name: ")


#File Configs
fileFormat = '.txt'

#Begin Program
file=open(fileName + fileFormat,'r') #Open the data file
data=file.readlines() #Load the entire file into memory
file.close() #close it

global frame

#Connect to the Device
dev.start()

print("Opening log file...")

for line in data: #Parse each line
    #Split each line at the comma
    message = line.rstrip('\n').split(',', 11)
    
    #build the can frame
    # Parse the id, create a frame
    #frame_id = int(message.id, 16)
    frame_id = int(message[1], 16)
    frame_id_hex = hex(frame_id)
        
    frame = can.Frame(frame_id)
    
    # Set our frame equal to message data
    frame.dlc = int(message[2])
    
    #convert list of nibbles from strings to ints    
    message_value = []
    message_value = map(int, message[3:11])
    #set out frames data to our new value
    frame.data = message_value
    
    #print raw from file
    #print(message)
    #print process frame ready to be sent
    print(frame)
    
    #send the can frame
    dev.send(frame)
    
print("Finished sending")
#dev.stop()
print("Connection Closed.")