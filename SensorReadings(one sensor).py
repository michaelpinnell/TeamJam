import spidev
import time
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
    #    for value in self:
         self[0]=ReadSensor(0)
#------------------------------------------------------------
class SensorReadings(dict):
    """Created when one of the sensors goes over the threshold set for recording"""
    def __init__(self,key):
        super(SensorReadings,self).__init__(key)
    def pprint(self):
        for key in sorted(self.iterkeys()):
            print key , self.get(key)
    def add_reading(self,reading):
        i=0
        for key in sorted(self.iterkeys()):
            self[key].append(reading[i])
            i+=1
#------------------------------------------------------------
#---------------User Defined Functions-----------------------
#This function was taken from http://www.raspberrypi-spy.co.uk/2013/10/analogue-sensors-on-the-raspberry-pi-using-an-mcp3008/ and is used here to convert the digital input from the ADC into a meaningful value between 0-1024 (10 bit ADC)
def ReadSensor(sensor):
    """sensor must be between 0-7 because our ADC has 8 analog inputs"""
    adc = spi.xfer2([1,(8 + sensor)<<4,0])
    data = ((adc[1] & 3) << 8) + adc[2]
    return data
#------------------------------------------------------------
def Poll(table,values):
    """Called to check if any sensor values are over the threshold, expects table to be a SensorReadings object and values to be a Reading object"""
    delay = 1
    values.update()
    for value in values:
        if int(value) > 250:
            table.add_reading(values)
            table.pprint()
            break
    time.sleep(delay)
#------------------------------------------------------------
#--------------------Main Control System---------------------
#First we initialize a Reading object to hold the values of our sensors and a SensorReadings object to store any values that are over the threshold
CurrentSensorValues = Reading([ReadSensor(0)])
SensorTable = SensorReadings({'Sensor 0' : []})
#Next we begin polling our sensors to see if any have broken the threshold
while True:
    Poll(SensorTable,CurrentSensorValues)
    
