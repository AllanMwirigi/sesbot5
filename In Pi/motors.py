import RPi.GPIO as gpio
import time

LMotor = 15
LMotor2 = 37
LMotorE = 10

RMotor = 11
RMotor2 = 40
RMotorE = 13

axleWidth = 14
#axleWidth = 9.5 use this constant for  red chasis
setSpeed = 30
rotspeed = 50
halfAxleW = 0.5 * axleWidth
#bias = 0.875 #calculated bias using gear ratios.
# bias = 0.8
bias = 1 #no bias on either wheel.
# jsDur = 0.08

# bias = 0.83
jsDur = 0.08

degpersec = 540.00

gpio.setmode(gpio.BOARD)

gpio.setup(LMotor, gpio.OUT)
gpio.setup(LMotorE, gpio.OUT)
gpio.setup(RMotor, gpio.OUT)
gpio.setup(RMotorE, gpio.OUT)

leftmotor = gpio.PWM(LMotorE, 500)
rightmotor = gpio.PWM(RMotorE, 500)
leftmotor.start(0)
rightmotor.start(0)

canJumpStart = True


def forward():
    global canJumpStart
    gpio.output(LMotor, False)
    gpio.output(RMotor, False)
    if canJumpStart == True:
        jumpStart(jsDur)

    # leftmotor.ChangeDutyCycle(setSpeed*bias)
    # rightmotor.ChangeDutyCycle(setSpeed)
    
    leftmotor.ChangeDutyCycle(setSpeed)    
    rightmotor.ChangeDutyCycle(setSpeed*bias)
    # time.sleep(4)
    # gpio.output(LMotor, True)
    # gpio.output(RMotor, True)

# ew
def reverse():
    global canJumpStart
    gpio.output(LMotor, True)
    gpio.output(RMotor, True)
    if canJumpStart == True:
        jumpStart(jsDur)

    # leftmotor.ChangeDutyCycle(setSpeed*bias)
    leftmotor.ChangeDutyCycle(setSpeed)    
    rightmotor.ChangeDutyCycle(setSpeed)

def curveLeft(r):
    global canJumpStart
    gpio.output(LMotor, False)
    gpio.output(RMotor, False)
    if canJumpStart == True:
        jumpStart(jsDur)

    rightmotor.ChangeDutyCycle(setSpeed)
    lws = setSpeed * (r-halfAxleW)/(r+halfAxleW)
    if lws < 0:
        lws = setSpeed

    leftmotor.ChangeDutyCycle(lws*bias)

def curveRight(r):
    global canJumpStart
    gpio.output(LMotor, False)
    gpio.output(RMotor, False)
    if canJumpStart == True:
        jumpStart(jsDur)

    leftmotor.ChangeDutyCycle(setSpeed*bias)
    rws = setSpeed * (r-halfAxleW)/(r+halfAxleW)
    if rws < 0:
        rws = setSpeed

    # rightmotor.ChangeDutyCycle(rws*bias)
    rightmotor.ChangeDutyCycle(rws)

def stop():
    print 'stopping motors'
    leftmotor.ChangeDutyCycle(0)
    rightmotor.ChangeDutyCycle(0)
    global canJumpStart
    canJumpStart = True


def jumpStart(dur):
    global canJumpStart
    print 'jump starting'
    canJumpStart = False
    leftmotor.ChangeDutyCycle(100*bias)
    rightmotor.ChangeDutyCycle(100)
    time.sleep(dur)

def rotateright(angle):
    global degpersec
    gpio.output(LMotor, False)
    gpio.output(RMotor, False)
    print '180'
    leftmotor.ChangeDutyCycle(rotspeed*bias)
    rightmotor.ChangeDutyCycle(0)
    time.sleep(angle/degpersec)
    stop()

def rotateleft(angle):
    global degpersec
    gpio.output(LMotor, False)
    gpio.output(RMotor, False)
    leftmotor.ChangeDutyCycle(0)
    rightmotor.ChangeDutyCycle(rotspeed)
    time.sleep(angle/degpersec)
    stop()

def maneuver():
    rotateright(50)
    curveLeft(17.00)
    time.sleep(2)
    rotateright(70)
    forward()
    time.sleep(0.5)
    stop()

#############################################
# functions for phonetilt as controller
def forwardTilt(angle):

    # ensure angle value does not exceed expected limits
    if(angle < -90):
        angle = -90
    if(angle > 90):
        angle = 90
    print angle

    # arbitrarily taken 70cm radius to give full revolution of robot
    # 90 degree tilt angle gives full revolution of robot, therefore determine the radius for each angle value
    r = angle*(70/90)

    if(angle < 0):     #turning left
        curveLeft(r)
    if(angle > 0):     #turning right
        curveRight(r)
    if(angle == 0):    #
        forward()

def reverseTilt(angle):
    # ensure angle value does not exceed expected limits
    if(angle < -90):
        angle = -90
    if(angle > 90):
        angle = 90

    # arbitrarily taken 70cm radius to give full revolution of robot
    # 90 degree tilt angle gives full revolution of robot, therefore determine the radius for each angle value
    r = angle*(70/90)

    if(angle < 0):     #turning right reversing
        curveRightReverse(r)
    if(angle > 0):     #turning left reversing
        curveLeftReverse(r)        
    if(angle == 0):    #
        reverse()

def curveLeftReverse(r):
    global canJumpStart
    gpio.output(LMotor, True)
    gpio.output(RMotor, True)
    if canJumpStart == True:
        jumpStart(jsDur)

    rightmotor.ChangeDutyCycle(setSpeed)
    lws = setSpeed * (r-halfAxleW)/(r+halfAxleW)
    if lws < 0:
        lws = setSpeed

    leftmotor.ChangeDutyCycle(lws*bias)

def curveRightReverse(r):
    global canJumpStart
    gpio.output(LMotor, True)
    gpio.output(RMotor, True)
    if canJumpStart == True:
        jumpStart(jsDur)

    leftmotor.ChangeDutyCycle(setSpeed*bias)
    rws = setSpeed * (r-halfAxleW)/(r+halfAxleW)
    if rws < 0:
        rws = setSpeed

    # rightmotor.ChangeDutyCycle(rws*bias)
    rightmotor.ChangeDutyCycle(rws)

# try:
#     # forward()
#     reverse()
#     time.sleep(4)
#     # reverse()
#     forward()
#     time.sleep(4)

#     gpio.cleanup()

# except:
#     gpio.cleanup()
