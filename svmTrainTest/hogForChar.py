# Import the modules
import cv2
from sklearn.externals import joblib
from skimage.feature import hog
import numpy as np
import argparse
from sklearn.svm import LinearSVC
from collections import Counter

import os
import fnmatch
list_hog_fd = []
responses = []
# Read the input image 
for dirpath, dirs, files in os.walk('/home/vaishthiru/Downloads/FinalProject/MyDataSet'):
    for filename in fnmatch.filter(files, '*.png'):
        #print (filename)
        keyVal = dirpath[dirpath.rindex('/')+1 : ]
        #print ("K="+keyVal)
        im = cv2.imread(dirpath+"/"+filename)

        im = cv2.resize(im,(180, 120), interpolation = cv2.INTER_CUBIC)
        # Convert to grayscale and apply Gaussian filtering
        im_gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        im_gray = cv2.GaussianBlur(im_gray, (5, 5), 0)
        #out = np.zeros(im.shape,np.uint8)
        # Threshold the image
        im_th = cv2.adaptiveThreshold(im_gray,255,1,1,11,2)
        #ret, im_th = cv2.threshold(im_gray, 90, 255, cv2.THRESH_BINARY_INV)

        # Find contours in the image
        _, ctrs, hier = cv2.findContours(im_th,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE )
#findContours( threshold_output, contours, hierarchy, CV_RETR_LIST, CV_CHAIN_APPROX_SIMPLE, Point(0, 0) );

        # Get rectangles contains each contour
        rects = [cv2.boundingRect(ctr) for ctr in ctrs]

        # For each rectangular region, calculate HOG features and predict
        # the digit using Linear SVM.
        
        for cnt in ctrs:
            if cv2.contourArea(cnt)>68:
                [x,y,w,h] = cv2.boundingRect(cnt)
                if  h>28:
                    cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),3)
                    roi = im_th[y:y+h,x:x+w]
                    roi = cv2.resize(roi, (28, 28), interpolation=cv2.INTER_AREA)
                    roi = cv2.dilate(roi, (3, 3))
                    roi_hog_fd = hog(roi, orientations=9, pixels_per_cell=(14, 14), cells_per_block=(1, 1), visualise=False)
                       
        key = ord(keyVal[0])
        responses.append(key)
        print (roi_hog_fd)
        print (keyVal[0])
        #cv2.imshow('im',im)
        #cv2.waitKey(0)
        list_hog_fd.append(roi_hog_fd)
        
hog_features = np.array(list_hog_fd, 'float32')
labels = np.array(responses, 'int')

# Create an linear SVM object
clf = LinearSVC()

# Perform the training
clf.fit(hog_features, labels)

# Save the classifier
joblib.dump(clf, "chars_cls.pkl", compress=3)

