"""
This file contains functions which deal with the images captured
"""

# Import the libraries
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from skimage import measure
from skimage.metrics import structural_similarity as compare_ssim
from skimage import color
import cv2.cv2


# Global vars for passing between functions
global FIG
global AX
global X_COORDS
global Y_COORDS

# Initial canvas crop returns the co-ordinates which all the images
# in the scene will be cropped to
def CanvasCrop(fileName):
    Img = cv2.imread(fileName)
    ax = plt.gca()
    plt.imshow(Img)
    plt.show()
    x_coords = ax.get_xlim()
    y_coords = ax.get_ylim()
    print("Final Coords = x:", x_coords, " and y:", y_coords)
    return x_coords, y_coords

# Debug image viewer (might be handy later with GUI)
def Img_View(Img):
    plt.imshow(Img)
    plt.show()

# Removes previously painted elements and returns image of newly
# painted element cropped
def ElementRemoval(NewImg, PrevImg):

    # Convert images to grayscale
    before_gray = color.rgb2grey(PrevImg)
    after_gray = color.rgb2grey(NewImg.copy())

    # Compute SSIM between two images
    (score, diff) = compare_ssim(before_gray, after_gray, full=True)
    diff = (diff * 255).astype("uint8")
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    
    gray = color.rgb2grey(thresh)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    contours = cv2.findContours(blurred, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]

    canvas = blurred.copy()
    H,W = blurred.shape[:2]
    AREA = H*W
    
    for c in contours:
        area = cv2.contourArea(c)
        if  AREA/100 < area < AREA/1:
            x, y, w, h = cv2.boundingRect(c)
            x = x - round((w*0.1)/2)
            y = y - round((h*0.1)/2)
            w = w + round((w*0.1))
            h = h + round((h*0.1))
            # Check if coords are negative (i.e. outside the canvas)
            if x < 0:
                x = 0
            elif y < 0:
                y = 0
            return NewImg[y:y+h, x:x+w]


    return NewImg

def InitialCrop(NewImg):

    Img = (NewImg * 255).astype("uint8")

    gray = color.rgb2grey(Img)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)

    contours = cv2.findContours(blurred, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2]
    
    canvas = blurred.copy()
    H,W = blurred.shape[:2]
    AREA = H*W
    
    for c in contours:
        area = cv2.contourArea(c)
        if  AREA/100 < area < AREA/1:
            x, y, w, h = cv2.boundingRect(c)
            x = x - round((w*0.1)/2)
            y = y - round((h*0.1)/2)
            w = w + round((w*0.1))
            h = h + round((h*0.1))
            return NewImg[y:y+h, x:x+w]

    return NewImg

