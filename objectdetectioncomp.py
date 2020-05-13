import cv2
import numpy as np
import urllib
from Queue import Queue
from threading import Thread

def nothing(x):
    pass

def url_image(url):
    #download the image, convert it to a numpy array, ad then read it into opencv
    trials = 0
    while(1):
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
                return 0,0;
            else:
                continue

def computePxToCm(px):
    pxToCmRatio = 0.1503
    return px * pxToCmRatio


cap = cv2.VideoCapture(0)

# cv2.namedWindow("trackbar")
# cv2.createTrackbar('Hmin','trackbar',0,255,nothing)
# cv2.createTrackbar('Hmax','trackbar',0,255,nothing)
# cv2.createTrackbar('Smin','trackbar',0,255,nothing)
# cv2.createTrackbar('Smax','trackbar',0,255,nothing)
# cv2.createTrackbar('Vmin','trackbar',0,255,nothing)
# cv2.createTrackbar('Vmax','trackbar',0,255,nothing)

focalLength = 600 #570  #laptop camera
counter = 0
objList = []
closestObjAtStart = None
distToClosest = None

while(1):

    # Success,feed = url_image('http://192.168.0.185:8080/shot.jpg')
    # if Success == 0:
    #     break

    ret,feed = cap.read()

    # Get dimensions of video feed   i.e.
    feedheight, feedwidth, channels = feed.shape

    # Draw line at centre of feed
    top_point = (feedwidth/2, 0)
    bottom_point = (feedwidth/2, feedheight)
    cv2.line(feed, top_point, bottom_point, (0,255, 255), 1)
    cv2.imshow('original', feed)

    blur = cv2.GaussianBlur(feed, (7,7), 0)
    feed2 = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    # cv2.imshow('original', feed2)

        
        # get current positions of trackbars
    Hmin = cv2.getTrackbarPos('Hmin','trackbar') #147
    Hmax = cv2.getTrackbarPos('Hmax','trackbar') #217   
    Smin = cv2.getTrackbarPos('Smin','trackbar') #80
    Smax = cv2.getTrackbarPos('Smax','trackbar') #255
    Vmin = cv2.getTrackbarPos('Vmin','trackbar') #0
    Vmax = cv2.getTrackbarPos('Vmax','trackbar') #144

    #green values 20,100  185,253  52,184
    #green values 43,118  69,160  118,235
    # 60,74,62,88,253,239
    
    # feedthrsh = cv2.inRange(feed2, np.array([Hmin,Smin,Vmin]), np.array([Hmax,Smax,Vmax]))
    feedthrsh = cv2.inRange(feed2, np.array([60,74,62]), np.array([88,253,239]))
        
    erodeKernel = np.ones((3,3), np.uint8, cv2.MORPH_RECT)
    dilateKernel = np.ones((8,8), np.uint8, cv2.MORPH_RECT)
    eroded = cv2.erode(feedthrsh, erodeKernel, iterations=2)
    dilated = cv2.dilate(eroded, dilateKernel, iterations=2)
    # cv2.imshow('thresholded2', dilated)

    _,contours,_ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    objFound = False
    
    # focal length calibration
    # c = max(contours, key=cv2.contourArea)
    # rect = cv2.minAreaRect(c)
    # box = cv2.boxPoints(rect)
    # box = np.int0(box)
    # cv2.drawContours(feed,[box],0,(0,255,0),2)
    # boxwidth, boxheight = rect[1]
    # a = a+1
    # if a%25 == 0:
    #     print boxwidth     

    for c in contours:
        
        if cv2.contourArea(c) > 1000:

            # determine objects with four points
            # epsilon = 0.05*cv2.arcLength(c,True)
            # approx = cv2.approxPolyDP(c,epsilon,True)
            # if len(approx) == 4:
            #     myCnt = approx

            rect = cv2.minAreaRect(c)
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(feed,[box],0,(0,255,0),2)

            # determine object centroid
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(feed, (cX, cY), 5, (20,100,200), 1, -1)

            # determine distance to object using relation D=(ActualWidth * FocalLength)/PixelWidth  from  F=(Px * D)/W
            boxwidth, boxheight = rect[1]
            objDist = (7.5*focalLength)/boxwidth  # try using heights
            # cv2.putText(feed, "{0:.2f} cm".format(objDist), (30, feed.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
            objFound = True
            
            # determine deviation of object centre from feed centre
            midwidth = feedwidth/2
            xdev = None
            if cX > midwidth:
                xdev = computePxToCm(cX - midwidth)
                cv2.line(feed, (midwidth, cY), (cX, cY), (0, 255, 255), 2)
                cv2.putText(feed, "{0:.2f} cm".format(xdev), (cX-50, cY-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (125, 0, 255), 1)

            elif cX < midwidth:
                xdev = computePxToCm(midwidth - cX)
                cv2.line(feed, (cX, cY), (midwidth, cY), (0, 255, 255), 2)
                cv2.putText(feed, "{0:.2f} cm".format(xdev), (cX+10, cY-5), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (125, 0, 255), 1)

            # store the initial object distances and other details
            pos = None
            objList.append([rect, objDist, xdev, pos])

    # determine the object closest to the camera
    if len(objList) != 0:
        closestObj = min(objList, key = lambda t: t[1])
        closestTop = closestObj[0][0][1] - (closestObj[0][1][1]/2) - 5
        # cv2.putText(feed, "closest", (int(closestObj[0][0][0]-5), int(closestTop)), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (125, 0, 255), 1)

        if counter < 2:
            closestObjAtStart = closestObj

        # Mark the objects
        for i, obj in enumerate(sorted(objList, key = lambda t: t[1])):
            cv2.putText(feed, "Object {0} : {1:.2f} cm".format(i, obj[1]), (30, feed.shape[0] - (50-(i*15))), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            obj[3] = i
            objTop = obj[0][0][1] - (obj[0][1][1]/2) - 5
            cv2.putText(feed, "Object {}".format(i), (int(obj[0][0][0]-5), int(objTop)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (125, 0, 255), 1)

            # keep track of reducing object distance of closest object
            if i == 0:
                # if distToClosest != None and distToClosest > obj[1]: # try to reduce interference from other object
                distToClosest = obj[1]

    if counter < 5:
        counter+=1

    objList[:] = []


    #if objFound == True:
        #print('Object detected')
        #camera stop rotating
        #bot and 
        #move towards it
        #motor.forward()

    cv2.imshow('bounded', feed)
                    
    if cv2.waitKey(10) == 27:
        break

cap.release()
cv2.destroyAllWindows()
