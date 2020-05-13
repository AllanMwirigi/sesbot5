
import cv2
import numpy as np
import urllib

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


cv2.namedWindow("trackbar")
cv2.createTrackbar('Hmin','trackbar',0,255,nothing)
cv2.createTrackbar('Hmax','trackbar',0,255,nothing)
cv2.createTrackbar('Smin','trackbar',0,255,nothing)
cv2.createTrackbar('Smax','trackbar',0,255,nothing)
cv2.createTrackbar('Vmin','trackbar',0,255,nothing)
cv2.createTrackbar('Vmax','trackbar',0,255,nothing)

while 1:
	# get current positions of trackbars

	success,feed = url_image('http://192.168.0.140:8080/shot.jpg')
	if success == 0:
		print 'Exiting'
		break

	blur = cv2.GaussianBlur(feed, (7,7), 0)
	feed2 = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

	Hmin = cv2.getTrackbarPos('Hmin','trackbar') #147
	Hmax = cv2.getTrackbarPos('Hmax','trackbar') #217   
	Smin = cv2.getTrackbarPos('Smin','trackbar') #80
	Smax = cv2.getTrackbarPos('Smax','trackbar') #255
	Vmin = cv2.getTrackbarPos('Vmin','trackbar') #0
	Vmax = cv2.getTrackbarPos('Vmax','trackbar') #144

	# 60,74,62,88,253,239
	feedthrsh = cv2.inRange(feed2, np.array([Hmin,Smin,Vmin]), np.array([Hmax,Smax,Vmax]))
	# feedthrsh = cv2.inRange(feed2, np.array([60,74,62]), np.array([88,253,239]))

	erodeKernel = np.ones((3,3), np.uint8, cv2.MORPH_RECT)
	dilateKernel = np.ones((8,8), np.uint8, cv2.MORPH_RECT)
	eroded = cv2.erode(feedthrsh, erodeKernel, iterations=2)
	dilated = cv2.dilate(eroded, dilateKernel, iterations=2)

	feed3, contours, heirarchy = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	objFound = False

	for c in contours:
	    if cv2.contourArea(c) > 1000:
	        epsilon = 0.05*cv2.arcLength(c,True)
	        approx = cv2.approxPolyDP(c,epsilon,True)
	        M = cv2.moments(approx)
	        rect = cv2.minAreaRect(c)
	        box = cv2.boxPoints(rect)
	        box = np.int0(box)
	        cv2.drawContours(feed,[box],0,(0,255,0),2)
	        objFound = True

	cv2.imshow('bounded', feed)

	if cv2.waitKey(10) == 27:
		break

cv2.destroyAllWindows()


        