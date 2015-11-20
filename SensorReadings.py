class Reading(list):
    def __init__(self,key):
        super(Reading,self).__init__(key)
    def update(self,key):
        super(Reading,self).__init__(key)
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
CurrentSensorValues = Reading([100,200,300]);
SensorTable = SensorReadings({'Sensor 1' : [],'Sensor 2' : [],'Sensor 3' : []})
SensorTable.add_reading(CurrentSensorValues)
SensorTable.pprint()
CurrentSensorValues.update([150,200,300]);
SensorTable.add_reading(CurrentSensorValues)
SensorTable.pprint()
