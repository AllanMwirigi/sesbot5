import cv2
import numpy as np
import urllib

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

a = 0

def findF(pxHeight):
	actualHeight = 21
	objDist = 75
	f = (objDist*pxHeight)/(actualHeight-pxHeight)
	return f

def findFF(pxHeight):
	actualHeight = 21
	feedHeightPx = 1080 #480 #800
	objDist = 75

	f = objDist/((actualHeight*feedHeightPx)/pxHeight)
	return f

def findS(pxHeight):
	actualHeight = 210
	feedHeightPx = 1600 #480 #800
	objDist = 750
	focalLength = 2.7

	s = (2.7*210*feedHeightPx)/(pxHeight*objDist)
	return s

def findSW(xdevPx):
	actualHeight = 210
	feedWidthPx = 1200 #480 #800
	objDist = 750
	focalLength = 2.7

	sw = (2.7*330*feedWidthPx)/(xdevPx*objDist)
	return sw


while 1:
	# success,feed = url_image('http://192.168.0.140:8080/frame.jpg')
	# success,feed = url_image('http://192.168.0.140:8080/shot.jpg')
	success,feed = url_image('http://192.168.1.107:8080/shot.jpg')
	if success == 0:
		print 'Exiting'
		break
	blur = cv2.GaussianBlur(feed, (7,7), 0)
	feed2 = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

	# feedthrsh = cv2.inRange(feed2, np.array([60,74,62]), np.array([88,253,239]))
	# feedthrsh = cv2.inRange(feed2, np.array([47,65,51]), np.array([90,155,136]))
	feedthrsh = cv2.inRange(feed2, np.array([33,65,51]), np.array([90,155,200]))
	    
	erodeKernel = np.ones((3,3), np.uint8, cv2.MORPH_RECT)
	dilateKernel = np.ones((8,8), np.uint8, cv2.MORPH_RECT)
	eroded = cv2.erode(feedthrsh, erodeKernel, iterations=2)
	dilated = cv2.dilate(eroded, dilateKernel, iterations=2)
	# cv2.imshow('thresholded2', dilated)

	_,contours,_ = cv2.findContours(dilated.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	objFound = False

	# for c in contours:
	# if cv2.contourArea(c) > 750:
	# focal length calibration
	c = max(contours, key=cv2.contourArea)
	x,y,w,h = cv2.boundingRect(c)
	cv2.rectangle(feed,(x,y),(x+w,y+h),(0,255,0),2)
	# rect = cv2.minAreaRect(c)
	# box = cv2.boxPoints(rect)
	# box = np.int0(box)
	# cv2.drawContours(feed,[box],0,(0,255,0),2)
	# boxwidth, boxheight = rect[1]
	# _,dimensions,_ = rect
	# boxwidth, boxheight = dimensions
	# print boxwidth, boxheight, 

	if a%5 == 0:
	    # print boxwidth, boxheight, findS(boxheight)  # 0.9866 #1.016 #0.9331
	    print w, h, findS(h)
	    # print boxheight  

	cv2.imshow('bounded', feed)
	a = a+1
	if cv2.waitKey(10) == 27:
		break

cv2.destroyAllWindows() 
	