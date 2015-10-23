import numpy as np
from scipy.interpolate import interp1d, InterpolatedUnivariateSpline
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap, BoundaryNorm
import matplotlib.path as path
from matplotlib.collections import LineCollection
import spidev
import time
#Set up plot
count=0
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
    def pprint(self):
        for key in sorted(self.iterkeys()):
            print key , self.get(key)
    def add_reading(self,reading):
        i=0
        for key in sorted(self.iterkeys()):
            self[key].append(reading[i])
            i+=1
    def copy(self,table):
        for key in sorted(self.iterkeys()):
            self[key]=table[key]
    def reset(self):
        for key in sorted(self.iterkeys()):
            self[key]=[]
    def plot(self):
        global count
        rmax=0
        rmin=1200
        i=0
        plt.figure(count)
        f, axarr = plt.subplots(len(self),sharex=True,sharey=True)
        f.suptitle('Reading ' + str(count),fontsize = 20)
        for key in sorted(self.iterkeys()):
            axarr[i].set_title(key)
            lc= coloredPlot(axarr[i],self[key],'b','y','r')
            lc.set_linewidth(3)
            i+=1
            if (min(self[key]) < rmin):
                rmin = min(self[key])
            if (max(self[key]) > rmax):
                rmax = max(self[key])
        f.text(0.03,0.6,'force level',rotation = 'vertical')
        plt.axis([0,len(self.values()[0]),rmin - 100,rmax + 100])
        plt.show()
        plt.savefig("Reading" + str(count) + ".png")
#------------------------------------------------------------
#---------------User Defined Functions-----------------------
#This function was taken from http://www.raspberrypi-spy.co.uk/2013/10/analogue-sensors-on-the-raspberry-pi-using-an-mcp3008/ and is used here to convert the digital input from the ADC into a meaningful value between 0-1024 (10 bit ADC)
def ReadSensor(sensor):
    """sensor must be between 0-7 because our ADC has 8 analog inputs"""
    adc = spi.xfer2([1,(8 + sensor)<<4,0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data
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
def coloredPlot(axes, reading,cold,warm,hot):
    x = range(0,len(reading))
    xi = np.linspace(0,len(reading),101)
    f = InterpolatedUnivariateSpline(x,reading)
    colormap = ListedColormap([cold,warm,hot])
    norm = BoundaryNorm([min(reading),300,650,max(reading)],colormap.N)
    points = np.array([xi,f(xi)]).T.reshape(-1,1,2)
    segments = np.concatenate([points[:-1], points[1:]], axis =1)
    lc = LineCollection(segments,cmap = colormap, norm = norm)
    lc.set_array(f(xi))
    axes.add_collection(lc)
    axes.set_xlim(0,len(x))
    axes.set_ylim(min(f(xi))-15,max(f(xi))+15)
    return lc
#------------------------------------------------------------
def Poll(table,values,bufferval):
    global count
    """Called to check if any sensor values are over the threshold, expects table to be a SensorReadings object and values to be a Reading object"""
    delay = 0.01
    values.update()
    if (len(table.values()[0]) == 0):
        delay = 0.1
        checkBuffer(bufferval)
        updateBuffer(bufferval,values)
    for value in values:
        if ((value > 650) or (table.state == 'triggered')):
            if (len(table.values()[0]) == 0):
                table.state = 'triggered'
                table.copy(bufferval)
            table.add_reading(values)
            if (len(table.values()[0]) >= 40):
                count+=1
                print str(count) + ": Current figure"
                #table.pprint()
                table.plot()
                table.reset()
                table.state = 'asleep' 
            break
    time.sleep(delay)
#------------------------------------------------------------
#--------------------Main Control System---------------------
#First we initialize a Reading object to hold the values of our sensors and a SensorReadings object to store any values that are over the threshold
CurrentSensorValues = Reading([ReadSensor(0),ReadSensor(1),ReadSensor(2)])#,ReadSensor(3),ReadSensor(4),ReadSensor(5),ReadSensor(6),ReadSensor(7)])
SensorTable = SensorReadings({'Sensor 0' : [],'Sensor 1' : [],'Sensor 2' : []})#,'Sensor 3' : [],'Sensor 4' : [],'Sensor 5' : [],'Sensor 6' : [],'Sensor 7' : []})
BufferTable = {'Sensor 0' : [],'Sensor 1' : [],'Sensor 2' : []}#,'Sensor 3' : [],'Sensor 4' : [],'Sensor 5' : [],'Sensor 6' : [],'Sensor 7' : []}
#Next we begin polling our sensors to see if any have broken the threshold
while True:
    Poll(SensorTable,CurrentSensorValues,BufferTable)
