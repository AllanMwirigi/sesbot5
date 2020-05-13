import cv2
import numpy as np
import urllib
import time

def url_image(url):
    #download the image, convert it to a numpy array, and then read it into opencv
    trials = 0
    try:
        resp = urllib.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype = "uint8")
        image = cv2.imdecode(image,cv2.IMREAD_COLOR)
        return (1,image)
    except IOError:
        #If an error is encountered, handle it.
        print("\n No connection could be made because the target machine actively refused it.Retrying...")
        trials = trials+1
        if trials == 5:
            print("\n Unable to communicate with IP camera. Please check your connection")
            return 0,0
        else:
            pass

focalLength = 2.7 #0.28#0.9331 #0.9866  #1.02
counter = 0
objList = []
closestObjAtStart = None
distToClosest = None
objIsFound = False
actualBoxHeight = 210
frameHeightPx = 1600
frameWidthPx = 1200
#frameHeightPx = 800
#frameWidthPx = 480
sensorHeight = 5.4 #10.5
sensorWidth = 4.582 #6.4216

def findXdev(pxXdev, dist):
    global focalLength
    global frameWidthPx
    global sensorWidth
    # xdev = (focalLength*actualBoxHeight*frameWidthPx)/(pxXdev*6.4216)
    xdev = (pxXdev*sensorWidth*dist)/(focalLength*frameWidthPx)
    return xdev

def findObjDist(pxHeight):
    # actualBoxHeight = 21
    # frameHeightPx = 800
    global actualBoxHeight
    global frameHeightPx
    global focalLength

    # dist = 0.5248*((actualBoxHeight*frameHeightPx)/pxHeight)
    #knowing this, try out xdev
    dist = (focalLength*actualBoxHeight*frameHeightPx)/(pxHeight*sensorHeight)
    # dist = (focalLength*actualBoxHeight)/pxHeight #fw/p
    return dist

def findSW(xdevPx):
    actualHeight = 210
    frameWidthPx = 1200 #480 #800
    objDist = 750
    focalLength = 2.7
    actualXdev = 210

    sw = (2.7*actualXdev*frameWidthPx)/(xdevPx*objDist)
    return sw

# def detect(outq):
def findObject():
    # focalLength = 80 #320 #310 #307-326
    global focalLength
    global counter
    global objList
    global closestObjAtStart
    global distToClosest
    global objIsFound

    success,frame = url_image('http://192.168.0.140:8080/shot.jpg')
    # success,frame = url_image('http://192.168.1.107:8080/shot.jpg')

    if success == 0:
        print 'no image'
        exit()

    # Get dimensions of video frame   i.e.
    frameheight, framewidth, channels = frame.shape
    # Draw line at centre of frame
    #top_point = (framewidth/2, 0)
    #bottom_point = (framewidth/2, frameheight)
    #cv2.line(frame, top_point, bottom_point, (0,255, 255), 1)

    blur = cv2.GaussianBlur(frame, (7,7), 0)
    frame2 = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

    # 60,74,62,88,253,239
    
    # framethrsh = cv2.inRange(frame2, np.array([60,74,40]), np.array([88,253,239])) #Anto's place
    framethrsh = cv2.inRange(frame2, np.array([76, 74, 40]), np.array([96, 253, 255]))  # Anto's place
    # framethrsh = cv2.inRange(frame2, np.array([56, 47, 0]), np.array([87, 199, 87]))  # My place daytime
    # framethrsh = cv2.inRange(frame2, np.array([56, 47, 20]), np.array([87, 199, 87]))  # My place daytime
    # framethrsh = cv2.inRange(frame2, np.array([33,65,51]), np.array([90,155,136]))
    
    #erodeKernel = np.ones((3,3), np.uint8, cv2.MORPH_RECT)
    #dilateKernel = np.ones((8,8), np.uint8, cv2.MORPH_RECT)
    #eroded = cv2.erode(framethrsh, erodeKernel, iterations=2)
    #dilated = cv2.dilate(eroded, dilateKernel, iterations=2)

    #_,contours,_ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    _,contours,_ = cv2.findContours(framethrsh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:
        return 'Nothing Found'

    else:
        c = max(contours, key=cv2.contourArea)

        if cv2.contourArea(c) < 1000:
            return 'Nothing Found'

        # object(s) of right size found
        else:
            x, y, boxwidth, boxheight = cv2.boundingRect(c)
            #cv2.rectangle(frame, (x, y), (x + boxwidth, y + boxheight), (0, 255, 0), 2)

            # determine object centroid
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            #cY = int(M["m01"] / M["m00"])
            #cv2.circle(frame, (cX, cY), 5, (20, 100, 200), 1, -1)

            # determine distance to closest object
            objDist = findObjDist(boxheight)
            # print objDist

            # determine deviation of object centre from frame centre
            midwidth = framewidth / 2
            xdev = None
            if cX > midwidth:
                xdev = findXdev(cX - midwidth, objDist)
                # print findSW(cX-midwidth)
                #cv2.line(frame, (midwidth, cY), (cX, cY), (0, 255, 255), 2)
                #cv2.putText(frame, "{0:.2f} mm".format(xdev), (cX - 50, cY - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(125, 0, 255), 1)

            elif cX < midwidth:
                xdev = findXdev(cX - midwidth, objDist)
                # print findSW(midwidth-cX)
                #cv2.line(frame, (cX, cY), (midwidth, cY), (0, 255, 255), 2)
                #cv2.putText(frame, "{0:.2f} mm".format(xdev), (cX + 10, cY - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4,(125, 0, 255), 1)

            elif cX == midwidth:
                xdev = 0

            if xdev != None and objDist != None:
                print 'Mapping : Image found'
                return xdev, objDist
        # if cv2.waitKey(10) == 27:
        #     cv2.destroyAllWindows()
        #     break