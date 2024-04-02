"""
This script should be able to be used for a performance and the gui can be added later
"""
# Import Libraries and functions
import os
import cv2.cv2
import ImageProcessing as IP
import PaintingMusicClasses as PMC

# Get user folder containing test images
FOLDER_PATH = './ImagePreprocessingTestImgs'

# List container for classes
PaintedObjects = []

# Go through each image in the folder
DIRECTORY = os.fsencode(FOLDER_PATH)
FILES = sorted(os.listdir(DIRECTORY))
IS_TITLE_PAGE = True
ITERATION = 0

for file in FILES:
     # Get the filename
    filename = os.fsdecode(file)
    filepath = os.path.join(FOLDER_PATH, filename)

    # Canvas Crop
    if IS_TITLE_PAGE:
        x_coords, y_coords = IP.CanvasCrop(filepath)
        IS_TITLE_PAGE = False
        x1 = int(round(x_coords[0]))
        x2 = int(round(x_coords[1]))
        y1 = int(round(y_coords[0]))
        y2 = int(round(y_coords[1]))

    # Get the new images
    NewImg = cv2.imread(filepath)
    NewImg = NewImg[y2:y1, x1:x2]
    
    if ITERATION > 1:
        # We need to remove previously painted elements and return new element cropped
        Img = IP.ElementRemoval(NewImg, PrevImg)
        IP.Img_View(Img)
        PaintedObject = PMC.PaintedObject(Img)
        print (PaintedObject.WinningNode)
        PaintedObjects.append(PaintedObject)

    PrevImg = NewImg
    ITERATION = ITERATION + 1
