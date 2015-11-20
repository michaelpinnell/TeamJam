try:
    import RPi.GPIO as GPIO
except RuntimeError:
    print "Error importin RPi.GPIO"
DEBUG=1
GPIO.setmode(GPIO.BCM)
def pollSensor (sensor):
    reading = 0
    GPIO.setup(sensor,GPIO.IN)
    while(reading < 10000):
        reading+=1
    return GPIO.input(sensor)
while True:
    print pollSensor(10)
