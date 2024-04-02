"""
This script contains functions which extract feature data to be passed into the SOM
"""
import cv2
import numpy as np


def FeatureExtraction(Img):
    # Extracting the colour intensity
    GreyLevels = np.histogram(cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY),10)[0]
    
    # Get the amount of space taken up by each object
    whitePixels = np.sum(cv2.cvtColor(Img, cv2.COLOR_BGR2GRAY) == 255)
    blackPixels = abs((Img.shape[0] * Img.shape[1]) - whitePixels)
    
    # Frequency analysis
    Freq = np.histogram(np.fft.fft2(Img),10)[0]
    
    # Append all the analysis to a feature row to be returned
    FeatureRow = []
    FeatureRow.append(GreyLevels)
    FeatureRow[0] = np.append(FeatureRow[0],whitePixels)
    FeatureRow[0] = np.append(FeatureRow[0],blackPixels)
    FeatureRow[0] = np.append(FeatureRow[0],Freq)
    
    return FeatureRow
    
