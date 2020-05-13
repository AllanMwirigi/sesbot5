import RPi.GPIO as GPIO
import time
import math
GPIO.setmode(GPIO.BOARD)

#stepPins = [7,8,5,3]
stepPins = [7,8,5,3]
stepdelay = 0.001
#degperstep = 5.625
degperstep = 0.087890625
currentangle = 0
lasthalfstep = 0; #the last half step to be performed.

for pin in stepPins:
    GPIO.setup(pin,GPIO.OUT)
    GPIO.output(pin,0)

seq = [ [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1],
        [1,0,0,1] ]

def makeCWstep():
    global lasthalfstep
    global currentangle
    if lasthalfstep == 7:
        lasthalfstep = 0
    else:
        lasthalfstep += 1
    for pin in range(4):
        GPIO.output(stepPins[pin],seq[lasthalfstep][pin])
    currentangle+=degperstep

def makeCCWstep():
    global lasthalfstep
    global currentangle
    if lasthalfstep == 0:
        lasthalfstep = 7
    else:
        lasthalfstep -= 1
    for pin in range(4):
        GPIO.output(stepPins[pin],seq[lasthalfstep][pin])
    currentangle-=degperstep

def CW(degrees):
    steps=int(degrees/degperstep)
    x = 0
    while x < steps:
        makeCWstep()
        time.sleep(stepdelay)
        x+=1
def CCW(degrees):
    steps=int(degrees/degperstep)
    x = 0
    while x < steps:
        makeCCWstep()
        time.sleep(stepdelay)
        x+=1

def home():
    global currentangle
    if currentangle > 0:
        CCW(currentangle)
    elif currentangle == 0:
        return
    elif currentangle < 0:
        CW(abs(currentangle))

#CCW(22.5)