# pi ip 192.168.0.196

# Approach 1: Keep objectdetection running on seperate thread as motors run
# Approach 2: Do detection, stop it, run motors with data obtained, restart detection

import mapping
import motors
import RPi.GPIO as gpio
import time
import stepper2 as stepper

lastdir = 'F'

kP = 127500.00
# kPL = 75000
# kPR = 120000
checkpoints = []

def xdevToRadius(xdev):
    if xdev < 0:
        r = abs(kP / xdev)
        direction = 'R'
    else:
        r = abs(kP / xdev)
        direction = 'L'
    return direction, r

# adjust motion when robot starts deviating
def adjustMotion(dir):
    if(dir == 'L'):         #adjust motion to go left a bit, as robot is deviating to the right
        motors.curveLeft(150)  # adjust this value till it gets really accurate
    if(dir == 'R'):         #adjust motion to go right a bit, as robot is deviating to the left
        motors.curveRight(150)

def nearestscan():
    print 'scanning for nearest'
    global checkpoints
    triedright = False
    triedleft = False
    counter = 0
    stepper.home()
    while stepper.currentangle <= 90:
        result = mapping.findObject()
        if result != 'Nothing Found':
            checkpoint = result[1],stepper.currentangle
            checkpoints.append(checkpoint)
        if stepper.currentangle != 90:
            stepper.CW(22.5)
            time.sleep(0.5)
        else:
            stepper.home()
            break
    while stepper.currentangle >= -90:
        result = mapping.findObject()
        if result != 'Nothing Found':
            checkpoint = result[1],stepper.currentangle
            checkpoints.append(checkpoint)
        if stepper.currentangle != -90:
            stepper.CCW(22.5)
            time.sleep(0.5)
        else:
            stepper.home()
            break
    if len(checkpoints) != 0:
        closest = [0,0]
        for x in range(len(checkpoints)):
            checkpoint = checkpoints[x]
            if x == 0:
                closest[1] = checkpoint[0]
            if checkpoint[0] < closest[1]:
                closest[1] = checkpoint[0]
                closest[0] = x
        checkpoint = checkpoints[closest[0]]
        return checkpoint[1]
    else:
        return


def stepperfind():
    print 'relocating object'
    triedright = False
    triedleft = False
    if lastdir == 'R':
        while mapping.findObject() == 'Nothing Found':
            if stepper.currentangle == 90 and not triedright:
                triedright = True
                stepper.home()
                print 'homing stepper'
            elif not triedright:
                stepper.CW(22.5)
                time.sleep(0.5)
                print 'turning clockwise'
            elif stepper.currentangle == -90:
                triedleft = True
                stepper.home()
                break
            elif not triedleft:
                stepper.CCW(22.5)
                time.sleep(0.5)
                print 'turning anticlockwise' 
    else:
        while mapping.findObject() == 'Nothing Found':
            if stepper.currentangle == -90 and not triedleft:
                triedleft = True
                stepper.home()
                print 'homing stepper'
            elif not triedleft:
                stepper.CCW(22.5)
                time.sleep(0.5)
                print 'turning anticlockwise'
            elif stepper.currentangle == 90:
                triedright = True
                stepper.home()
                break
            elif not triedright:
                stepper.CW(22.5)
                time.sleep(0.5)
                print 'turning anticlockwise' 

    if triedleft and triedright:
        print 'No object in sight, perhaps behind'
        stepper.home()
        return
    else:
        print 'objectfound at angle {0}'.format(stepper.currentangle)
        angle = stepper.currentangle
        stepper.home()
        return angle

#stepper.CW(90)
#exit()

stepperfile = open("stepper.txt", "r")
stepperAngle = float(stepperfile.read())
stepperfile.close()
print "THIS IS STEPPER ANGLE ", stepperAngle 
stepper.currentangle = stepperAngle
stepper.home()


searchtrials = 0
lostobject = 0
try:
    while True:
        checkpoints[:] = []
        search = nearestscan() 
        print search
        if search == None:
            if searchtrials == 4:
                print 'no object found'
                exit()
            else:
                print 'looking behind'
                motors.rotateright(180)
                searchtrials += 1
                continue
        searchtrials = 0
        if search > 0:
            print 'rotating right to {0}'.format(search)
            motors.rotateright(search)
        elif search < 0:
            print 'rotating left to {0}'.format(search)
            motors.rotateleft(abs(search))

        res = mapping.findObject()
        objDist = res[1]
        print 'starting'

        while objDist > 350:
            result = mapping.findObject()
            if result != 'Nothing Found' and result != 'Object too small':
                xdev, dist = result
                objDist = dist
                if xdev == 0:
                    # motors move straight ahead
                    motors.forward()
                else:
                    if(xdev < -250):
                        print 'Robot deviating right, adjusting to left'
                        adjustMotion('L')
                    elif(xdev > 250):
                        print 'Robot deviating left, adjusting to right'                        
                        adjustMotion('R')
                    else:
                        direction, radius = xdevToRadius(xdev)

                        if direction == 'L':
                            print'curving left', radius
                            motors.curveLeft(radius)
                            if lastdir != 'L' :
                                lastdir = 'L'
                        else:
                            print'curving right', radius
                            motors.curveRight(radius)
                            if lastdir != 'R':
                                lastdir = 'R'
            else:
                print 'Object lost'
                motors.stop()
                search = stepperfind() 
                print search
                if search == None:
                    lostobject = True
                    break
                elif search > 0:
                    print 'rotating right to {0}'.format(search)
                    motors.rotateright(search)
                elif search < 0:
                    print 'rotating left to {0}'.format(search)
                    motors.rotateleft(abs(search))
       
        if lostobject == True:
            lostobject = False
            continue
        motors.stop()
        time.sleep(3)
        motors.maneuver()

except (KeyboardInterrupt,Exception) as e:
    print e
    print 'cleaning up'
    gpio.cleanup()
    stepperfile = open('stepper.txt','w')
    stepperfile.write(str(stepper.currentangle))
    stepperfile.close()



