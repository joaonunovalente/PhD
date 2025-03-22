#!/usr/bin/env python

import open3d as o3d
import cv2 as cv
import numpy
import sys
numpy.set_printoptions(threshold=sys.maxsize)

filename = '/home/valente/Documents/vscode/PhD-code/kinect2/data/color/0001.png'

# image = cv.imread(filename)
image = cv.imread(filename)
# print(image)

# image = image[:,:10]
print(image[:,620:])
# image1 = image[:,:630]

# while True:
#     cv.imshow('Original', image)
#     cv.imshow('Processed', image16)

#     if cv.waitKey(10) == 27:
#         break   


# cv.imwrite('blog/example6/uint11.png', image)
# cv.imwrite('blog/example6/uint16.png', image16)
# print(image)
# print(image[:,630:])