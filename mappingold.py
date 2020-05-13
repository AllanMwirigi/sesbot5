import cv2
import numpy as np
import urllib
import time
# 1.8 - 3.2
def url_image(url):
    # download the image, convert it to a numpy array, ad then read it into opencv
    trials = 0
    try:
        resp = urllib.urlopen(url)
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return (1, image)
    except IOError:
        # If an error is encountered, handle it.
        print("\n No connection could be made because the target machine actively refused it.Retrying...")
        trials = trials + 1
        if trials == 5:
            print("\n Unable to communicate with IP camera. Please check your connection")
            return 0, 0
        else:
            pass


focalLength = 2.7  # 0.28#0.9331 #0.9866  #1.02
counter = 0
objList = []
closestObjAtStart = None
distToClosest = None
objIsFound = False
actualBoxHeight = 210
frameHeightPx = 1600
frameWidthPx = 1200
sensorHeight = 5.4  # 10.5
sensorWidth = 4.582  # 6.4216


def computePxToCm(px):
    pxToCmRatio = 2.58  # 1.264
    return px * pxToCmRatio


def findXdev(pxXdev, dist):
    global focalLength
    global frameWidthPx
    global sensorWidth
    # xdev = (focalLength*actualBoxHeight*frameWidthPx)/(pxXdev*6.4216)
    xdev = (pxXdev * sensorWidth * dist) / (focalLength * frameWidthPx)
    return xdev


def findObjDist(pxHeight):
    # actualBoxHeight = 21
    # frameHeightPx = 800
    global actualBoxHeight
    global frameHeightPx
    global focalLength

    # dist = 0.5248*((actualBoxHeight*frameHeightPx)/pxHeight)
    # knowing this, try out xdev
    dist = (focalLength * actualBoxHeight * frameHeightPx) / (pxHeight * sensorHeight)
    # dist = (focalLength*actualBoxHeight)/pxHeight #fw/p
    return dist


def findSW(xdevPx):
    actualHeight = 210
    frameWidthPx = 1200  # 480 #800
    objDist = 750
    focalLength = 2.7
    actualXdev = 210

    sw = (2.7 * actualXdev * frameWidthPx) / (xdevPx * objDist)
    return sw

def nothing(x):
    pass

# def detect(outq):
def findObject():
    # focalLength = 80 #320 #310 #307-326
    global focalLength
    global counter
    global objList
    global closestObjAtStart
    global distToClosest
    global objIsFound

    cv2.namedWindow("trackbar")
    cv2.createTrackbar('Hmin','trackbar',0,180,nothing)
    cv2.createTrackbar('Smin','trackbar',0,255,nothing)
    cv2.createTrackbar('Vmin','trackbar',0,255,nothing)
    cv2.createTrackbar('Hmax','trackbar',0,180,nothing)
    cv2.createTrackbar('Smax','trackbar',0,255,nothing)
    cv2.createTrackbar('Vmax','trackbar',0,255,nothing)

    while 1:
        success, frame = url_image('http://192.168.0.120:8080/shot.jpg')
        startT = time.time()
        # success, frame = url_image('http://192.168.1.107:8080/shot.jpg')
        if success == 0:
            print ('No image')
            exit()

        # Get dimensions of video frame   i.e.
        frameheight, framewidth, channels = frame.shape
        # Draw line at centre of frame
        top_point = (framewidth / 2, 0)
        bottom_point = (framewidth / 2, frameheight)
        cv2.line(frame, top_point, bottom_point, (0, 255, 255), 1)

        #blur = cv2.GaussianBlur(frame, (7, 7), 0)
        #frame2 = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        frame2 = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        Hmin = cv2.getTrackbarPos('Hmin', 'trackbar')  # 147
        Smin = cv2.getTrackbarPos('Smin', 'trackbar')  # 80
        Vmin = cv2.getTrackbarPos('Vmin', 'trackbar')  # 0
        Hmax = cv2.getTrackbarPos('Hmax', 'trackbar')  # 217
        Smax = cv2.getTrackbarPos('Smax', 'trackbar')  # 255
        Vmax = cv2.getTrackbarPos('Vmax', 'trackbar')  # 144

        # 60,74,62,88,253,239
        
        #framethrsh = cv2.inRange(frame2, np.array([60, 74, 40]), np.array([88, 253, 239])) #Anto's place
        framethrsh = cv2.inRange(frame2, np.array([76, 74, 0]), np.array([96, 253, 255]))  # Anto's place        
        # framethrsh = cv2.inRange(frame2, np.array([56, 47, 0]), np.array([87, 199, 87])) #My place daytime
        #framethrsh = cv2.inRange(frame2, np.array([76, 74, 40]), np.array([96, 253, 255])) #Kenya High     
        # framethrsh = cv2.inRange(frame2, np.array([56, 47, 20]), np.array([87, 199, 87])) #My place daytime
        #framethrsh = cv2.inRange(frame2, np.array([Hmin,Smin,Vmin]), np.array([Hmax,Smax,Vmax])) #tune colour
        # erodeKernel = np.ones((3, 3), np.uint8, cv2.MORPH_RECT)
        # dilateKernel = np.ones((8, 8), np.uint8, cv2.MORPH_RECT)
        # eroded = cv2.erode(framethrsh, erodeKernel, iterations=2)
        # dilated = cv2.dilate(eroded, dilateKernel, iterations=2)

        _, contours, _ = cv2.findContours(framethrsh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # oldLoop(contours, frame, framewidth)
        # stopT = time.time()
        # print stopT - startT

        if len(contours) != 0:
            c = max(contours, key=cv2.contourArea)
            if cv2.contourArea(c) > 1000:
                x, y, boxwidth, boxheight = cv2.boundingRect(c)
                hwRatio = float(boxheight)/float(boxwidth)
                if hwRatio > 1.8 and hwRatio < 3.2:
                    cv2.rectangle(frame, (x, y), (x + boxwidth, y + boxheight), (0, 255, 0), 2)
                    # print hwRatio
                    # determine object centroid
                    M = cv2.moments(c)
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                    cv2.circle(frame, (cX, cY), 5, (20, 100, 200), 1, -1)

                    # determine distance to closest object
                    objDist = findObjDist(boxheight)
                    # print objDist

                    # determine deviation of object centre from frame centre
                    midwidth = framewidth / 2
                    xdev = None
                    if cX > midwidth:
                        xdev = findXdev(cX - midwidth, objDist)
                        # print findSW(cX-midwidth)
                        cv2.line(frame, (midwidth, cY), (cX, cY), (0, 255, 255), 2)
                        cv2.putText(frame, "{0:.2f} mm".format(xdev), (cX - 50, cY - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                                    (125, 0, 255), 1)

                    elif cX < midwidth:
                        xdev = findXdev(cX - midwidth, objDist)
                        # print findSW(midwidth-cX)
                        cv2.line(frame, (cX, cY), (midwidth, cY), (0, 255, 255), 2)
                        cv2.putText(frame, "{0:.2f} mm".format(xdev), (cX + 10, cY - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                                    (125, 0, 255), 1)

                    elif cX == midwidth:
                        xdev = 0

                    # if xdev != None and objDist != None:
                    #     return (xdev, objDist)

        cv2.imshow('bounded', frame)

        if cv2.waitKey(10) == 27:
            cv2.destroyAllWindows()
            break


def oldLoop(contours, frame, framewidth):
    global focalLength
    global counter
    global objList
    global closestObjAtStart
    global distToClosest
    global objIsFound

    for c in contours:

        if cv2.contourArea(c) > 1000:
            # print cv2.contourArea(c)

            # determine objects with four points
            # epsilon = 0.05*cv2.arcLength(c,True)
            # approx = cv2.approxPolyDP(c,epsilon,True)
            # if len(approx) == 4:
            #     myCnt = approx

            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(frame,[box],0,(0,255,0),2)
            # x, y, boxwidth, boxheight = cv2.boundingRect(c)
            # cv2.rectangle(frame, (x, y), (x + boxwidth, y + boxheight), (0, 255, 0), 2)

            # determine object centroid
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(frame, (cX, cY), 5, (20, 100, 200), 1, -1)

            # determine distance to object using relation D=(ActualWidth * FocalLength)/PixelWidth  from  F=(Px * D)/W
            boxwidth, boxheight = rect[1]          #remove these two lines
            # objDist = (21*focalLength)/boxheight
            objDist = findObjDist(boxheight)
            # print objDist
            cv2.putText(frame, "{0:.2f} cm".format(objDist), (30, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                        (0, 0, 255), 1)

            # determine deviation of object centre from frame centre
            midwidth = framewidth / 2
            xdev = None
            if cX > midwidth:
                xdev = findXdev(cX - midwidth, objDist)
                # print findSW(cX-midwidth)
                cv2.line(frame, (midwidth, cY), (cX, cY), (0, 255, 255), 2)
                cv2.putText(frame, "{0:.2f} mm".format(xdev), (cX - 50, cY - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                            (125, 0, 255), 1)

            elif cX < midwidth:
                xdev = findXdev(cX - midwidth, objDist)
                # print findSW(midwidth-cX)
                cv2.line(frame, (cX, cY), (midwidth, cY), (0, 255, 255), 2)
                cv2.putText(frame, "{0:.2f} mm".format(xdev), (cX + 10, cY - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                            (125, 0, 255), 1)

                # store the initial object distances and other details
                pos = None
                objList.append([rect, objDist, xdev, pos])

            # determine the object closest to the camera
            if len(objList) != 0:
                closestObj = min(objList, key = lambda t: t[1])
                closestTop = closestObj[0][0][1] - (closestObj[0][1][1]/2) - 5
                # cv2.putText(frame, "closest", (int(closestObj[0][0][0]-5), int(closestTop)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (125, 0, 255), 1)

                if counter == 3:
                    closestObjAtStart = closestObj
                    # outq.put(closestObj)
                elif counter < 3:
                    pass
                    # outq.put('Wait')

                # Mark the objects
                for i, obj in enumerate(sorted(objList, key = lambda t: t[1])):
                    cv2.putText(frame, "Object {0} : {1:.2f} cm".format(i, obj[1]), (30, frame.shape[0] - (50-(i*15))), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
                    obj[3] = i
                    objTop = obj[0][0][1] - (obj[0][1][1]/2) - 5
                    cv2.putText(frame, "Object {}".format(i), (int(obj[0][0][0]-5), int(objTop)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (125, 0, 255), 1)
                    # print obj[1]

                    # keep track of reducing object distance of closest object
                    if i == 0:
                        # if distToClosest != None and distToClosest > obj[1]: # try to reduce interference from other object
                        distToClosest = obj[1]

            if counter < 5:
                counter+=1

            objList[:] = []

            if closestObjAtStart == None:
                pass
                # outq.put('Nothing')

            #TODO  # When bot reaches target, get frameback from mainthread and reset the counter to initiate the process again

    cv2.imshow('bounded', frame)

findObject()
