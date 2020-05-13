import requests
import motors
lastmotion = 'X'
while True:
    # response = requests.get("http://192.168.1.105:3000/get")
    response = requests.get("http://192.168.0.170:3000/get")    
    command = response.json()
    motion = command['currentmotion']   
    angle = command['rotAngle'] 

    if motion == 'S':
        print 'stop'
        motors.stop()

    if motion == 'F':
        print 'forward'        
        motors.forwardTilt(angle)

    if motion == 'B':
        print 'reverse'        
        motors.reverseTilt(angle)
