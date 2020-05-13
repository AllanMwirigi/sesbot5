import ptvsd
ptvsd.enable_attach(secret = None)

import numpy as np
import cv2
import urllib
import requests
import time
import RPi.GPIO as GPIO
import math
import thread

GPIO.setmode(GPIO.BOARD)

#general constants
startoff = 1
findcheck = 2
gotocheck = 3
gohome = -1
checkcount = 0
action = findcheck #initialize the first action to be performed as startoff

###################################################################################
#The following defines functions related to physical movement of th robot

#variables to store the GPIO pins used for the motor driver
enableL = 23
logic1L = 19    #Left motor pins
logic2L = 21
GPIO.setup(enableL,GPIO.OUT)
GPIO.setup(logic1L,GPIO.OUT)
GPIO.setup(logic2L,GPIO.OUT)

enableR = 18
logic1R = 16    #right motor pins
logic2R = 22
GPIO.setup(enableR,GPIO.OUT)
GPIO.setup(logic1R,GPIO.OUT)
GPIO.setup(logic2R,GPIO.OUT)

pwmR = GPIO.PWM(enableR,1000)
pwmL = GPIO.PWM(enableL,1000)

#Stepper initialisation
coil_A_1_pin = 35
coil_A_2_pin = 37
coil_B_1_pin = 32
coil_B_2_pin = 38

GPIO.setup(coil_A_1_pin, GPIO.OUT)
GPIO.setup(coil_A_2_pin, GPIO.OUT)
GPIO.setup(coil_B_1_pin, GPIO.OUT)
GPIO.setup(coil_B_2_pin, GPIO.OUT)

camangle = 0;
laststep = 0;
degperstep = 5.625

#robot related constants
w = 10              #width of wheelbase
cm_per_sec = 3      #linear speed at 100% duty
angletime = 0.25    #time taken to rotate 1degree at 50% duty and radius 0

#define a class that stores the relative motion of the robot.
class motion:
    function = "stationary"     #what motion is being excecuted.
    speed = 0                   #what is the speed of the fastest wheel.
    radius = None               #if the motion is a curve, what is the radius
    duration = 0                #how long this state of motion has been held. Only used in last motion object
    starttime = time.time()     #what time did this motion start.

class coordinate:
    x = 0;
    y = 0;

botdirection = 0;


currentmotion = motion()
lastmotion = motion()
map = []            #this list stores all the motions of type motion in order to have a rough idea of location
checkpoints = []    #this list stores the checkpoint locations in terms of x and y coordinates.

def stepforward(delay, steps):  
  for i in range(0, steps):
    setStep(1, 0, 1, 0)
    time.sleep(delay)
    setStep(0, 1, 1, 0)
    time.sleep(delay)
    setStep(0, 1, 0, 1)
    time.sleep(delay)
    setStep(1, 0, 0, 1)
    time.sleep(delay)

def stepbackward(delay, steps):  
  for i in range(0, steps):
    setStep(1, 0, 0, 1)
    time.sleep(delay)
    setStep(0, 1, 0, 1)
    time.sleep(delay)
    setStep(0, 1, 1, 0)
    time.sleep(delay)
    setStep(1, 0, 1, 0)
    time.sleep(delay)

def setStep(w1, w2, w3, w4):
  GPIO.output(coil_A_1_pin, w1)
  GPIO.output(coil_A_2_pin, w2)
  GPIO.output(coil_B_1_pin, w3)
  GPIO.output(coil_B_2_pin, w4)

def camerapan(angle,waittime):
    global camangle
    steps = (angle - camangle)/degperstep
    if steps<0 :
        stepforward(int(waittime)/1000,abs(steps))
    elif steps>0 :
        stepbackward(int(waittime)/1000,abs(steps))
    camangle = math.asin(math.sin(degtorad(angle)))
    
def stepradar():
    delay = 10/1000
    global camangle
    global found
    stepcounter = 0
    while not found:
        setStep(1, 0, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 1, 0)
        time.sleep(delay)
        setStep(0, 1, 0, 1)
        time.sleep(delay)
        setStep(1, 0, 0, 1)
        time.sleep(delay)
        stepcounter += 4
    camangle += stepcounter * degperstep
    camangle = math.asin(math.sin(degtorad(camangle)))

def stationary():
    global currentmotion
    global lastmotion
    if currentmotion.function == "stationary":
        return
    GPIO.output(logic1L,0)
    GPIO.output(logic2L,0)
    GPIO.output(logic1R,0)
    GPIO.output(logic2R,0)
    lastmotion = currentmotion
    lastmotion.duration = time.time()-currentmotion.starttime
    map.append(lastmotion)  #add the last motion to the map.

    currentmotion.function = "stationary"
    currentmotion.speed = 0
    currentmotion.radius = None
    currentmotion.starttime = time.time()

def forward(speed):
    global currentmotion
    global lastmotion
    if currentmotion.function == "forward" and currentmotion.speed == speed:
        return
    pwmL.ChangeDutyCycle(speed)
    pwmR.ChangeDutyCycle(speed)
    GPIO.output(logic1L,1)
    GPIO.output(logic2L,0)
    GPIO.output(logic1R,1)
    GPIO.output(logic2R,0)
    lastmotion = currentmotion
    lastmotion.duration = time.time()-currentmotion.starttime
    map.append(lastmotion)  #add the last motion to the map.
    
    currentmotion.function = "forward"
    currentmotion.speed = speed
    currentmotion.radius = None
    currentmotion.starttime = time.time()

def reverse(speed):
    global lastmotion
    global currentmotion
    if currentmotion.function == "reverse" and currentmotion.speed == speed:
        return
    pwmL.ChangeDutyCycle(speed)
    pwmRChangeDutyCycle(speed)
    GPIO.output(logic1L,0)
    GPIO.output(logic2L,1)
    GPIO.output(logic1R,0)
    GPIO.output(logic2R,1)
    lastmotion = currentmotion
    lastmotion.duration = time.time()-currentmotion.starttime
    map.append(lastmotion)  #add the last motion to the map.

    currentmotion.function = "reverse"
    currentmotion.speed = speed
    currentmotion.radius = None
    currentmotion.starttime = time.time()

def curveleft(r,speed):
    global currentmotion
    global lastmotion
    if currentmotion.function == "curveleft" and currentmotion.speed == speed and currentmotion.radius == r:
        return
    lws = (r-w/2)*speed/(r+w/2)
    pwmR.ChangeDutyCycle(speed)
    pwmL.ChangeDutyCycle(round(abs(lws)))
    GPIO.output(logic1R,1)
    GPIO.output(logic2R,0)
    if lws < 0:
        GPIO.output(logic1L,0)
        GPIO.output(logic2L,1)
    else:
        GPIO.output(logic1L,1)
        GPIO.output(logic2L,0)
    lastmotion = currentmotion
    lastmotion.duration = time.time()-currentmotion.starttime
    map.append(lastmotion)  #add the last motion to the map.

    currentmotion.function = "curveleft"
    currentmotion.speed = speed
    currentmotion.radius = r
    currentmotion.starttime = time.time()

def curveright(r,speed):
    global currentmotion
    global lastmotion
    if currentmotion.function == "curveright" and currentmotion.speed == speed and currentmotion.radius == r:
        return
    rws = (r-w/2)*speed/(r+w/2)
    pwmL.ChangeDutyCycle(speed)
    pwmR.ChangeDutyCycle(round(abs(rws)))
    GPIO.output(logic1L,1)
    GPIO.output(logic2L,0)
    if rws < 0:
        GPIO.output(logic1R,0)
        GPIO.output(logic2R,1)
    else:
        GPIO.output(logic1R,1)
        GPIO.output(logic2R,0)
    lastmotion = currentmotion
    lastmotion.duration = time.time()-currentmotion.starttime
    map.append(lastmotion)  #add the last motion to the map.

    currentmotion.function = "curveright"
    currentmotion.speed = speed
    currentmotion.radius = r
    currentmotion.starttime = time.time()

def goaround():
    curveright(0,50)
    time.sleep(90*angletime)
    curveleft(10,50)
    time.sleep(3)
    curveright(0,1)
def rotatetocam():
    if camangle > 0:
        curveright(0,50)
        time.sleep(angletime*camangle)
        stationary()
    elif camangle < 0:
        curveleft(0,50)
        time.sleep(-angletime*camangle)
        stationary()
    else:
        return
    camerapan(0)

def dutytospeed(speed):
    return speed*cm_per_sec/100
def degtorad(deg):
    return deg*3.141592654/180
def radtodeg(rad):
    return rad*180/3.141592654

def location():   
    direction = 90   #variable to hold direction for each motion sequence, 0 is grid EAST CCW is positive.
    X = 0
    Y = 0
    for curve in map:
        if curve.function == "stationary":
            continue
        elif curve.function == "forward":
            s = curve.duration * dutytospeed(curve.speed)
            sX = s*math.cos(degtorad(direction))
            sY = s*math.sin(degtorad(direction))
            X += sX
            Y += sY
        elif curve.function == "reverse":
            s = curve.duration * dutytospeed(curve.speed)
            sX = s*math.cos(degtorad(180-direction))
            sY = s*math.sin(degtorad(180-direction))
            X += sX
            Y += sY
        elif curve.function == "curveleft":
            s = curve.duration * dutytospeed(curve.speed)
            rads = s/(curve.radius+0.5*w)
            sX = curve.radius*(math.cos(degtorad(direction-90)) + math.cos(degtorad(270-direction)-rads))
            sY = curve.radius*(math.sin(degtorad(270-direction)-rads) - math.sin(degtorad(direction-90)))
            X -= sX
            Y -= sX
            direction = direction + radtodeg(rads)
        elif curve.function == "curveright":
            s = curve.duration * dutytospeed(curve.speed)
            rads = s/(curve.radius+0.5*w)
            sX = curve.radius*(math.cos(degtorad(90-direction)) + math.cos(degtorad(90+direction)-rads))
            sY = curve.radius*(math.sin(degtorad(90+direction)-rads) - math.sin(degtorad(90-direction)))
            X += sX
            Y += sX
            direction = 360-radtodeg(rads)+direction
    return (X,Y,direction)

#create a fucntion to store the current location as a checkpoint.
def checkstore():
    check = coordinate()
    (check.x,check.y,_)=location()
    checkpoints.append(check)

#function to investigate if spotted checkpoint has already been found.
def ischecked(distance,xdev):
    global checkcount
    if checkcount == 0:
        return False
    location = coordinate()
    inspectionzone = coordinate()
    (location.x,location.y,direction) = location()  #first determine the current location
    lookangle = direction + camangle                #lookangle is the camera angle w.r.t the grid system
    sx = distance*math.cos(degtorad(lookangle))-xdev*math.cos(degtorad(270-lookangle))
    sy = distance*math.sin(degtorad(lookangle))+xdev*math.sin(degtorad(270-lookangle))
    (inspectionzone.x,inspectionzone.y) = (location.x + sx,location.y + sy)
    for c in checkpoints:
        if (c.x - 30) <= inspectionzone.x <= (c.x + 30) and (c.y - 30) <= inspectionzone.y <= (c.y + 30):
            return True
    return False

####################################################################################
#the following code is related to image processing

focallength = 625   #this is the focal length of the camera in use
checkheight = 20    #the known height of the checkpoints
homeheight = 40     #the known height of the home beacon
ipurl = 'http://192.168.1.101/live'
found = 0           #flag raised when a checkpoint is found

while(True):
    #wait for the ip camera to go online
    try:
        stream = requests.get(ipurl,stream=True)
        bytes = b''
        print('Connected to IP camera')
        break
    except:
        time.sleep(0.5)
        print('No cam yet')
        pass

def object_distance(knownheight,pixelheight):
    #compute and return the distance from the marker to the camera using triangle similarity
    if pixelheight:
        return knownheight * focallength / pixelheight
    else:
        return -1

def find_checkpoint(image):
    #first convert the image into HSV format
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    #define the HSV upper and lower limits of the color we want to detect
    #H:0-179    #S:0-255    #V:0-255
    lower = np.array([50,100,100]) # Lower green
    upper = np.array([85,255,255]) # Upper green
    mask = cv2.inRange(hsv,lower,upper)
    #draw some contours around the objects in the specified color range and show the image
    (_,cnts,_ )= cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if cnts:
        c = max(cnts,key = cv2.contourArea)
        rect = cv2.minAreaRect(c)
        Zcm = object_distance(checkheight,rect[1][1])       #compute the object's distance
        if 0 < Zcm < 300 :
            pix_frm_cent = (rect[0][0]-(np.size(image,1)/2))    #compute the number of pixels between the object center and the image center.
            Xcm = pix_frm_cent*Zcm/focallength                  #compute the actual distance from the center
            box = np.int0(cv2.boxPoints(rect))                  #draw a bounding box around the object and display it
            cv2.drawContours(image, [box], -1, (220,184,4),2)
            cv2.rectangle(image,(image.shape[1]-455,image.shape[0]),(image.shape[1]-180,image.shape[0]-55),(0,0,0),-1)
            cv2.putText(image, "Dist=%.2fcm" %Zcm, 
                       (image.shape[1] - 450, image.shape[0]-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1,(220,184,4),2)
            cv2.putText(image, "XDev=%.2fcm" %Xcm,
                        (image.shape[1]-450,image.shape[0]-30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,(220,184,4),2)
            cv2.circle(image,(int(rect[0][0]),int(rect[0][1])),7,(220,184,4), -1)
            cv2.imshow("image", image)
            cv2.waitKey(1)
            return (rect,Zcm,Xcm)
        else:        
            cv2.imshow("image",image)
            cv2.waitKey(1)
            return (0,0,0)
    else:
        cv2.imshow("image",image)
        cv2.waitKey(1)
        return (0,0,0)

def find_home(image):
    #first convert the image into HSV format
    hsv = cv2.cvtColor(image,cv2.COLOR_BGR2HSV)
    #define the HSV upper and lower limits of the color we want to detect
    #H:0-179    #S:0-255    #V:0-255
    lower = np.array([0,100,100]) # Lower red
    upper = np.array([20,255,255]) # Upper red
    mask = cv2.inRange(hsv,lower,upper)
    #draw some contours around the objects in the specified color range and show the image
    (_,cnts,_ )= cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    if cnts:
        c = max(cnts,key = cv2.contourArea)
        rect = cv2.minAreaRect(c)
        Zcm = object_distance(homeheight,rect[1][1])       #compute the object's distance
        if 0 < Zcm < 300 :
            pix_frm_cent = (rect[0][0]-(np.size(image,1)/2))    #compute the number of pixels between the object center and the image center.
            Xcm = pix_frm_cent*Zcm/focallength                  #compute the actual distance from the center
            box = np.int0(cv2.boxPoints(rect))                  #draw a bounding box around the object and display it
            cv2.drawContours(image, [box], -1, (220,184,4),2)
            cv2.rectangle(image,(image.shape[1]-455,image.shape[0]),(image.shape[1]-180,image.shape[0]-55),(0,0,0),-1)
            cv2.putText(image, "Dist=%.2fcm" %Zcm, 
                       (image.shape[1] - 450, image.shape[0]-5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1,(220,184,4),2)
            cv2.putText(image, "XDev=%.2fcm" %Xcm,
                        (image.shape[1]-450,image.shape[0]-30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1,(220,184,4),2)
            cv2.circle(image,(int(rect[0][0]),int(rect[0][1])),7,(220,184,4), -1)
            cv2.imshow("image", image)
            cv2.waitKey(1)
            return (rect,Zcm,Xcm)
        else:        
            cv2.imshow("image",image)
            cv2.waitKey(1)
            return (0,0,0)
    else:
        cv2.imshow("image",image)
        cv2.waitKey(1)
        return (0,0,0)

def dist_from_center(image,rectangle):
    bx = rectangle[0][0]
    by = rectangle[0][1]
    imgxcenter = np.size(image,1)/2
    imgycenter = np.size(image,0)/2
    sx = bx-imgxcenter
    sy = by-imgycenter    
    return (sX,sY)

#imgcap = cv2.VideoCapture('http://192.168.1.101/live.mjpg')
while (True):
    #first retrieve the imgae from the camera
    # When nothing is seen there is a divide by zero error, so this skips over those frames
    #bytes+=stream.raw.read(16384)
    #a = bytes.find(b'\xff\xd8')
    #b = bytes.find(b'\xff\xd9')
    #if a!=-1 and b!=-1:
    #    jpg = bytes[a:b+2]
    #    bytes= bytes[b+2:]
    #    frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
    #    image = frame
    #    (checkpoint,distance,xdev) = find_checkpoint(image)
    #else:
    #    continue 

    if action == startoff:
        forward(50)
        time.sleep(2)
        action = findcheck
    elif action == findcheck:
        found = 0
        thread.start_new_thread(stepradar,()) #rotates stepper like a radar on different thread
        while not found:
            bytes+=stream.raw.read(16384)
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')
            if a!=-1 and b!=-1:
                jpg = bytes[a:b+2]
                bytes= bytes[b+2:]
                frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
                image = frame
            else:
                continue
            (checkpoint,distance,xdev) = find_checkpoint(image)
            if checkpoint:
                print("found a checkpoint")
                if not ischecked(distance,xdev): #investigate if it was found
                    found = 1
                    action = gotocheck
    elif action == gotocheck:
        rotatetocam()
        k = 1000 #proportional correction constant
        distance = 400
        while distance > 10:
            bytes+=stream.raw.read(16384)
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')
            if a!=-1 and b!=-1:
                jpg = bytes[a:b+2]
                bytes= bytes[b+2:]
                frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
                image = frame
            else:
                continue
            (_,distance,xdev) = find_checkpoint(image)
            if xdev == 0:
                forward(50)
            elif xdev < 0:
                curveleft(k/abs(xdev),50)
            elif xdev > 0:
                curveright(k/xdev,50)
        checkcount +=1
        checkstore()
        if checkcount == 5:
            action = gohome
        else:
            action = findcheck
            goaround()  #go around the current checkpoint.
    elif action == gohome:
        (gridx,gridy,dir)=location()
        s = math.sqrt(gridx * gridx + gridy * gridy)
        T_angle = radtodeg(math.atan(degtorad(-1/(gridy/gridx))))
        if T_angle < dir :
            curveright(0,50)
            time.sleep(dir-T_angle * angletime)
        elif T_angle > dir:
            curveleft(0,50)
            time.sleep(T_angle-dir * angletime)
        curveleft(s/2,50)
        time.sleep(angletime*180)
        stationary()
        #lets look for the start point
        found = 0
        thread.start_new_thread(stepradar,()) #rotates stepper like a radar on different thread
        while not found:
            bytes+=stream.raw.read(16384)
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')
            if a!=-1 and b!=-1:
                jpg = bytes[a:b+2]
                bytes= bytes[b+2:]
                frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
                image = frame
            else:
                continue
            (home,distance,xdev) = find_home(image)
            if home:
                print("found home")
                found = 1
        #go to the startpoint
        rotatetocam()
        k = 1000 #proportional correction constant
        distance = 400
        while distance > 10:
            bytes+=stream.raw.read(16384)
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')
            if a!=-1 and b!=-1:
                jpg = bytes[a:b+2]
                bytes= bytes[b+2:]
                frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8),cv2.IMREAD_COLOR)
                image = frame
            else:
                continue
            (_,distance,xdev) = find_home(image)
            if xdev == 0:
                forward(50)
            elif xdev < 0:
                curveleft(k/abs(xdev),50)
            elif xdev > 0:
                curveright(k/xdev,50)


        