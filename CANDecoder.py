"""

Title: Dodge CAN Decoder
Desc: 
Version: 0.2
Release Notes:
Original Authors: http://tucrrc.utulsa.edu/DodgeCAN.html
Further Modifications by: Jean-Claude Thibault, Liam O'Brien

This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.
For a full copy of the license please vist this website: http://creativecommons.org/licenses/by-nc-sa/4.0/

"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

global pp
global basePath
pp=PdfPages('results/test.pdf')
basePath = 'results/'
fileName = 'CAN6/TestDrive.txt'

file=open(fileName,'r') #opens the data file
data=file.readlines() #Load the entire file into memory
file.close()

frame_id_filter = ['e','102','106','108','116','125','126','154','168','1f8','202','210','212','218','222','22c','2ac','2c8','2bc','238','312','3d8']
SHOW_ALL_IDs = True

#initialize variables
times=[]
IDs=[]
DLCs=[]
payloads=[]
hexpayloads=[]
IDLengths={}

for line in data[10:]: #Parse each line
    #Split each line where the commas are. This may need to be tab characters if the data was tab delimited
    entries=line.split(',')
    #print entries #(only for debugging)

    #convert timestamp (hours:minutes:seconds:millis:micros) into plain seconds
    #timestamp=entries[0]
    #timeParts=timestamp.split(':')
    #time=float(timeParts[0])*3600 + float(timeParts[1])*60 + float(timeParts[2]) + float(timeParts[3])*0.001 + float(timeParts[4])*0.000001
    time=float(entries[0])
    #print time
    times.append(time)

    #build a list of IDs
    identifier=entries[1]
    id_dec = int(identifier,16)
    identifier = hex(id_dec)[2:]

    if (identifier in frame_id_filter) or SHOW_ALL_IDs:
    
        IDs.append(identifier)
    
        dataLengthCode=int(entries[2],16)
        DLCs.append(dataLengthCode)
    
        #Build the IDLength dictionary
        IDLengths[identifier]=int(dataLengthCode)
        
        #parse the message 3-10
        #message=entries[6].split(' ')
        data=[]
        hexdata=[]
        message=[]
        #for d in message:
        #    data.append(int(d,16))
        for i in range(0, dataLengthCode):
            if entries[3+i]=='':
                chunk=0
            else:
                chunk = int(entries[3+i])
            data.append(chunk)
            message.append(hex(chunk)[2:])
        #print data
        payloads.append(data)
        hexpayloads.append(message)
    else:
        print 'Skipped 0x%s - ' %identifier


#Data Length Analysis for each ID

print 'CAN ID (Hex) -> Data Length'
IDList=IDLengths.keys()
IDList.sort()
for key in IDList:
    print key+' -> %g' %IDLengths[key]
   
#print 'CAN ID (Dec) -> Data Length'
#for key in IDList:
#    print `int(key,16)`+' -> %g' %IDLengths[key]   


#Timing Analysis
print 'CAN ID (Hex) -> Counts Per time (Hz) or '
results=open(basePath + 'results.html','w')
results.write('''<table border="1" cellspacing="1" cellpadding="2">
  <tr>
    <th scope="col">CAN ID (Hex)</th>
    <th scope="col">CAN ID (Dec)</th>
    <th scope="col">Data Length</th>
    <th scope="col">Frequency (Hz)</th>
    <th scope="col">Period (sec.)</th>
    <th scope="col">Notes</th>
 
  </tr>
  ''')

totalTime=float(times[-1]-times[0])
for key in IDList:
    occurances=IDs.count(key)
    print key+' -> %g Hz or %g sec' %((occurances/totalTime),totalTime/float(occurances))
    results.write(' <tr>\n    <td>%s</td>\n    <td>%g</td>\n    <td>%g</td>\n    <td>%g</td>\n    <td>%g</td>\n    <td>&nbsp;</td>\n  </tr>\n' %(key,int(key,16),IDLengths[key],(occurances/totalTime),totalTime/float(occurances)))
results.write('</table>\n')
results.close()


#calculate number of Bytes
totalBytes=0
for key in IDList:
    totalBytes+=int(IDLengths[key])
print 'There are %g unique IDs in the log file' %len(IDLengths)
print 'Total number of bytes to examine in the log: %g' %totalBytes

def plotDataCharvsTime(ID,times=times,IDs=IDs,data=payloads,IDLengths=IDLengths):
    X=[]
    Y_lsb=[]
    Y_msb=[]
    startTime=times[0]
    endTime=times[-1]
    for location in range(IDLengths[ID]):
        Y_lsb.append([])
        Y_msb.append([])
    for i,t,d in zip(IDs,times,data):
        if i==ID:
            X.append(t)
            for location in range(len(Y_lsb)):
                value = "{0:08b}".format(d[location])[2:]
                lsb = int(value[4:],2)
                msb = int(value[0:3],2)
                Y_lsb[location].append(lsb)
                Y_msb[location].append(msb)
    for location in range(IDLengths[ID]):
        outputName='Time History of CAN ID %s for byte %g 4-LSB' %(ID,location)
        plt.plot(X,Y_lsb[location],'-',rasterized=True)
        plt.xlim( startTime, endTime )
        plt.title(outputName)
        plt.ylabel('Value')
        plt.xlabel('Time [sec]')
        #plt.savefig(basePath + outputName+'.png')
        #plt.savefig(basePath + outputName+'.pdf')
        pp.savefig()
        plt.close()
        print 'File %s was written.' %outputName
        
        outputName='Time History of CAN ID %s for byte %g 4-MSB' %(ID,location)
        plt.plot(X,Y_msb[location],'-',rasterized=True)
        plt.xlim( startTime, endTime )
        plt.title(outputName)
        plt.ylabel('Value')
        plt.xlabel('Time [sec]')
        #plt.savefig(basePath + outputName+'.png')
        #plt.savefig(basePath + outputName+'.pdf')
        pp.savefig()
        plt.close()
        print 'File %s was written.' %outputName

def plotDatavsTime(ID,times=times,IDs=IDs,data=payloads,IDLengths=IDLengths):
        X=[]
        Y=[]
        startTime=times[0]
        endTime=times[-1]
        for location in range(IDLengths[ID]):
            Y.append([])
        for i,t,d in zip(IDs,times,data):
            if i==ID:
                X.append(t)
                for location in range(len(Y)):
                    Y[location].append(d[location])
        for location in range(IDLengths[ID]):
            outputName='Time History of CAN ID %s for byte %g' %(ID,location)
            plt.plot(X,Y[location],'-',rasterized=True)
            #plt.xlim( startTime, endTime )
            plt.title(outputName)
            plt.ylabel('Value')
            plt.xlabel('Time [sec]')
            #plt.savefig(basePath + outputName+'.png')
            #plt.savefig(basePath + outputName+'.pdf')
            pp.savefig()
            plt.close()
            
            print 'File %s was written.' %outputName
                  


    
def plotEvenDatavsTime(ID,times=times,IDs=IDs,data=payloads,IDLengths=IDLengths):
        bits=16
        X=[]
        Y=[]
        startTime=times[0]
        endTime=times[-1]
        for location in range(0,IDLengths[ID]-1,2):
            #print location
            Y.append([])
        
        for i,t,d in zip(IDs,times,data):
            if i==ID:
                X.append(t)
                #print d
                for location in range(len(Y)):
                    try:
                        #binaryString='%s' %bin(int(d[2*location]+d[2*location+1],16))[2:]
                        #THISONEbinaryString='%s' %bin( int( (d[2*location+1]*256) + d[2*location] ,16) )[2:]
                        #Y[location].append( int(binaryString[-(bits-1):],2) )
                        #THISONEY[location].append( float(int(binaryString[0:bits],2)/100) )
                        value = float( (d[2*location+1]*256.0+d[2*location])/1.0 )
                        Y[location].append(value)
                        #if location==1 and value>390 and value<395:
                        #    print '%3.2f' %value

                    except IndexError:
                        print 'Something is screwy in plotEvenDatavsTime! location=%s' %location
                        #print location
                        #print d
                        Y.pop(location)
                        pass
                    
        for location in range(len(Y)):
            outputName='Time History of CAN ID %s for (b%gx256 + b%g) using %g bits' %(ID,2*location+1,2*location,bits)
            #outputName='Time History of CAN ID %s for bytes %g and %g' %(ID,2*location,2*location+1)
            plt.figure(1)
            #plt.subplot(111)
            plt.plot(X,Y[location],'-',rasterized=True)
            #plt.xlim( startTime, endTime )
            plt.title(outputName)
            plt.ylabel('Value')
            plt.xlabel('Time [sec]')
            #plt.savefig(basePath + outputName+'.png')
            #plt.savefig(basePath + outputName+'.pdf')
            pp.savefig()
            plt.close()
            
            print 'File %s was written.' %outputName
                  

def plotOddDatavsTime(ID,times=times,IDs=IDs,data=payloads,IDLengths=IDLengths):
        bits=16
        X=[]
        Y=[]
        startTime=times[0]
        endTime=times[-1]
        for location in range(1,IDLengths[ID]-1,2):
            #print location
            Y.append([])
        for i,t,d in zip(IDs,times,data):
            if i==ID:
                X.append(t)
                for location in range(len(Y)):
                    try:
                        #ORIGINAL binaryString='%s' %bin(int(d[2*location]+d[2*location+1],16))[2:]
                        #ORIGINALY[location].append(int(binaryString[-(bits-1):],2))
                        value = float( (d[2*location+2]*256.0+d[2*location+1])/100.0 )
                        Y[location].append(value)

                    except IndexError:
                        Y.pop(location)
                        print 'Something is wrong.'
                        pass
        for location in range(len(Y)):
            outputName='Time History of CAN ID %s for bytes %g and %g using %g bits' %(ID,2*location+2,2*location+1,bits)
            outputName='Time History of CAN ID %s for bytes %g and %g' %(ID,2*location,2*location+1)
            plt.plot(X,Y[location],'-',rasterized=True)
            plt.xlim( startTime, endTime )
            plt.title(outputName)
            plt.ylabel('Value')
            plt.xlabel('Time [sec]')
            #plt.savefig(basePath + outputName+'.png')
            #plt.savefig(basePath + outputName+'.pdf')
            pp.savefig()
            plt.close()
            
            print 'File %s was written.' %outputName
print IDList                      
for key in IDList:
#for key in [ '222','22c','2ac','412','6f2','71c','79c']:
#for key in [ '222']:
    if key in IDList:
        plotDatavsTime(key)
        #plotDataCharvsTime(key)
        plotEvenDatavsTime(key) # This one
        #plotOddDatavsTime(key)
        print 'Done Plotting Data for '+key
            
pp.close()
print 'All done!'
