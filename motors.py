import RPi.GPIO as gpio
import sys
import time
import Tkinter as tk
#import ultrasound

LMotor = 15
LMotor2 = 37
LMotorE = 10

RMotor = 11
RMotor2 = 40
RMotorE = 13

axleWidth = 9.5
setSpeed = 10
halfAxleW = 0.5*axleWidth

gpio.setmode(gpio.BOARD)

gpio.setup(LMotor, gpio.OUT)
gpio.setup(LMotorE, gpio.OUT)
gpio.setup(RMotor, gpio.OUT)
gpio.setup(RMotorE, gpio.OUT)

leftmotor=gpio.PWM(LMotorE, 60)
rightmotor=gpio.PWM(RMotorE, 60)

def forward():
    leftmotor.start(setSpeed)
    rightmotor.start(setSpeed)
    gpio.output(LMotor, True)
    gpio.output(RMotor, True)

def reverse(dur):
    leftmotor.start(setSpeed)
    rightmotor.start(setSpeed)
    gpio.output(LMotor, False)
    gpio.output(RMotor, False)

def curveLeft(r):
    rightmotor.ChangeDutyCycle(setSpeed)
    lws = setSpeed * (r-halfAxleW)/(r+halfAxleW)
    leftmotor.ChangeDutyCycle(lws)

def curveRight(r):
    leftmotor.ChangeDutyCycle(setSpeed)
    rws = setSpeed * (r-halfAxleW)/(r+halfAxleW)
    rightmotor.ChangeDutyCycle(rws)

def stopMotors():
    leftmotor.ChangeDutyCycle(0)
    rightmotor.ChangeDutyCycle(0)

# try:
#     forward(3)

#     # turnLeft(1)

#     forward(3)

#     # reverse(5)
    
#     gpio.cleanup()
    
# except:
#     gpio.cleanup()
