import numpy as np
from scipy.interpolate import interp1d, InterpolatedUnivariateSpline
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.path as path
from matplotlib.collections import LineCollection
import spidev
import time
import os
import signal
#Set up plot
count=0
buffercount = 0
#Set up spi in order to use our A/D converter
spi = spidev.SpiDev()
spi.open(0,0)
#------------------------------------------------------------
#-----------------Class definitions--------------------------
#------------------------------------------------------------
class Reading(list):
    """Created to hold each of the sensors current value"""
    def __init__(self,key):
        super(Reading,self).__init__(key)
    def update(self):
        for i in range(0,len(self)):
            self[i]=ReadSensor(i)
#------------------------------------------------------------
class SensorReadings(dict):
    """Created when one of the sensors goes over the threshold set for recording"""
    def __init__(self,key):
        super(SensorReadings,self).__init__(key)
        self.state='asleep'
        self.stored = 0
    def pprint(self):
        for key in sorted(self.iterkeys()):
            print key , self.get(key)
    def add_reading(self,reading):
        i=0
        for key in sorted(self.iterkeys()):
            self[key].append(reading[i])
            i+=1
        self.stored = len(self.values()[0])
    def copy(self,table):
        for key in sorted(self.iterkeys()):
            self[key]=table[key]
    def reset(self):
        for key in sorted(self.iterkeys()):
            self[key]=[]
            self.stored = 0
    def plot(self):
        global count
        rmax=0
        rmin=1200
        i=0
        j=0
        plt.figure(count)
        print 'Plotting Figure %d'%count
        f, axarr = plt.subplots(4,2,sharex=True,sharey=True)
        f.suptitle('Reading ' + str(count),fontsize = 20)
        for key in sorted(self.iterkeys()):
            if i == 4:
                j+=1
                i = 0
            print 'Setting up subplot for %s'%(key)
            axarr[i,j].set_title(key)
            lc= coloredPlot(axarr[i,j],self[key],'b','y','r')
            lc.set_linewidth(2)
            i+=1
            if (min(self[key]) < rmin):
                rmin = min(self[key])
            if (max(self[key]) > rmax):
                rmax = max(self[key])
        f.text(0.03,0.6,'force level',rotation = 'vertical')
        plt.axis([0,self.stored,rmin-15,rmax+100])
        plt.show()
        print 'Saving Figure'
        f.savefig("Reading" + str(count) + ".png")
        print 'Done Saving Figure'
        self.reset()
        os.kill(os.getpid(),signal.SIGTERM)
#------------------------------------------------------------
#---------------User Defined Functions-----------------------
#This function was taken from http://www.raspberrypi-spy.co.uk/2013/10/analogue-sensors-on-the-raspberry-pi-using-an-mcp3008/ and is used here to convert the digital input from the ADC into a meaningful value between 0-1024 (10 bit ADC)
def ReadSensor(sensor):
    """sensor must be between 0-7 because our ADC has 8 analog inputs"""
    adc = spi.xfer2([1,(8 + sensor)<<4,0])
    data = ((adc[1] & 3) << 8) + adc[2]
    force = calcForce(data)
    return force
#------------------------------------------------------------
def calcForce(data):
    global f
    return f(data)
#------------------------------------------------------------
def checkBuffer(table):
    while(len(table.values()[0]) >= 10):
        for i in range(0,len(table)):
            del table.values()[i][0]
#------------------------------------------------------------
def updateBuffer(table,values):
    i=0
    for key in sorted(table.iterkeys()):
        table[key].append(values[i])
        i+=1
#------------------------------------------------------------
def initBuffer(table):
    for key in sorted(table.iterkeys()):
        for i in range (0,10):
            table[key].append(0)
#------------------------------------------------------------
def coloredPlot(axes,reading,cold,warm,hot):
    x = range(0,len(reading))
    xi = np.linspace(0,len(reading),101)
    f = InterpolatedUnivariateSpline(x,reading)
    colormap = ListedColormap([cold,warm,hot])
    norm = BoundaryNorm([min(reading)-100,300,650,max(reading)+100],colormap.N)
    points = np.array([xi,f(xi)]).T.reshape(-1,1,2)
    segments = np.concatenate([points[:-1], points[1:]], axis =1)
    lc = LineCollection(segments,cmap = colormap, norm = norm)
    lc.set_array(f(xi))
    axes.add_collection(lc)
    axes.set_xlim(0,len(x))
    axes.set_ylim(min(f(xi)),max(f(xi))+15)
    return lc
#------------------------------------------------------------
def Poll(table,values,bufferval):
    global buffercount
    global count
    """Called to check if any sensor values are over the threshold, expects table to be a SensorReadings object and values to be a Reading object"""
    delay = 0.01
    values.update()
    if (table.state == 'asleep'):
        buffercount+=1
        if buffercount >= 10:
            buffercount = 0
            checkBuffer(bufferval)
            updateBuffer(bufferval,values)
    for value in values:
        if ((value > 650) or (table.state == 'triggered')):
            if (table.state == 'asleep'):
                table.state = 'triggered'
                table.copy(bufferval)
            table.add_reading(values)
            print 'Table now has %d values in it'%table.stored
            checklength(table) 
            break
    time.sleep(delay)
#------------------------------------------------------------
def checklength(table):
    global count
    if (table.stored == 40):
        count+=1
        table.state = 'asleep'
        proc_num = os.fork()
        if proc_num == 0:
            table.plot()
        else:
            table.reset()
    elif (table.stored > 40):
        table.reset()
#-----------------------------------------------------------
def createBestfit():
    #input experimental values here
    points= np.array[(first resistance, first force),...]
    x = points[:,0]
    y = points[:,1]
    z = np.bpolyfit(x,y,3)
    f = np.poly1d(z)
    return f
#-----------------------------------------------------------
#--------------------Main Control System---------------------
#First we initialize a Reading object to hold the values of our sensors and a SensorReadings object to store any values that are over the threshold
f = createBestfit()
start = time.time()
CurrentSensorValues = Reading([ReadSensor(0),ReadSensor(1),ReadSensor(2),ReadSensor(3),ReadSensor(4),ReadSensor(5),ReadSensor(6),ReadSensor(7)])
SensorTable = SensorReadings({'Sensor 0' : [],'Sensor 1' : [],'Sensor 2' : [],'Sensor 3' : [],'Sensor 4' : [],'Sensor 5' : [],'Sensor 6' : [],'Sensor 7' : []})
BufferTable = {'Sensor 0' : [],'Sensor 1' : [],'Sensor 2' : [],'Sensor 3' : [],'Sensor 4' : [],'Sensor 5' : [],'Sensor 6' : [],'Sensor 7' : []}
initBuffer(BufferTable)
elapsedtime = 0
#Next we begin polling our sensors to see if any have broken the threshold
while True:
    currenttime=time.time()
    Poll(SensorTable,CurrentSensorValues,BufferTable)
    
    if (currenttime - start > 360):
        break
