import time
import RPi.GPIO as GPIO
#import objectdetection

GPIO.setmode(GPIO.BOARD)

# Define GPIO signals to use
# Pins 32, 37, 38, 35
# GPIO12, GPIO26, GPIO20, GPIO21
#stepPins = [12,26,20,19] # CW rotation
 

seq = [ [1,0,0,0],
        [1,1,0,0],
        [0,1,0,0],
        [0,1,1,0],
        [0,0,1,0],
        [0,0,1,1],
        [0,0,0,1],
        [1,0,0,1] ]

def anticlock(inq):
    stepPins = [32,35,37,38]
    #stepPins = [12,19,20,26]   #BCM

    for pin in stepPins:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0)
        
    #complete revolution - 512    #half revolution - 256
    c = None
    for i in range(128):
        sig = inq.get()
        for halfstep in range(8):
            #gothrough each half step
            for pin in range(4):
                GPIO.output(stepPins[pin],seq[halfstep][pin])
                print('turning anticlockwise')
            time.sleep(0.001)
        c = i
            
        if sig is _found:
            GPIO.cleanup()
            break

    reset1(c)

def reset1(t):
    stepPins = [38,37,35,32]

    for pin in stepPins:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0)
        
    #complete revolution - 512    #half revolution - 256
    for i in range(t):
        for halfstep in range(8):
            #gothrough each half step
            for pin in range(4):
                GPIO.output(stepPins[pin],seq[halfstep][pin])
                print('turning clockwise')
            time.sleep(0.001)

def clock(inq):
    stepPins = [38,37,35,32]

    for pin in stepPins:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0)

    c = None
    #complete revolution - 512    #half revolution - 256
    for i in range(128):
        sig = inq.get()
        for halfstep in range(8):
            #gothrough each half step
            for pin in range(4):
                GPIO.output(stepPins[pin],seq[halfstep][pin])
                print('turning clockwise')
            time.sleep(0.001)
        c = i

        if sig is _found:
            GPIO.cleanup()
            break

    reset2(c)

def reset2(t):
    stepPins = [32,35,37,38]

    for pin in stepPins:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0)
        
    #complete revolution - 512    #half revolution - 256
    for i in range(t):
        for halfstep in range(8):
            #gothrough each half step
            for pin in range(4):
                GPIO.output(stepPins[pin],seq[halfstep][pin])
                print('turning anticlockwise')
            time.sleep(0.001)


def test():
    stepPins = [7,8,5,3]
    #stepPins = [12,19,20,26]   #BCM

    for pin in stepPins:
        GPIO.setup(pin,GPIO.OUT)
        GPIO.output(pin,0)
        
    #complete revolution - 512    #half revolution - 256
    #for i in range(512):
    while 1:
        for halfstep in range(8):
            #gothrough each half step
            for pin in range(4):
                GPIO.output(stepPins[pin],seq[halfstep][pin])
                print('turning anticlockwise')
            time.sleep(0.001)
            
    GPIO.cleanup()

#test() 

