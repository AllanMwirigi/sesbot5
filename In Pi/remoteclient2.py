import requests
import motors
lastmotion = 'X'
while True:
    # response = requests.get("http://192.168.1.105:3000/get")
    response = requests.get("http://192.168.0.170:3000/get")    
    command = response.json()
    motion = command['currentmotion']    
    if motion != lastmotion:
        lastmotion = motion
        if motion == 'S':
            print 'stop'
            motors.stop()
        elif motion == 'R':
            print 'right'
            motors.curveRight(80)
        elif motion == 'L':
            print 'left'
            motors.curveLeft(80)
        elif motion == 'F':
            print 'forward'
            motors.forward()
        elif motion == 'B':
            print 'reverse'
            motors.reverse()
