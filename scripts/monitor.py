# import numpy as np
import numpy as np
import cv2
import math
import imutils
from array import array
from skimage.metrics import structural_similarity as compare_ssim
from sklearn.cluster import DBSCAN
import time
import random
from queue import Queue
import asyncio
import random
from Zoomer import Zoomer
from OBSChannel import OBSChannel

loop = asyncio.get_event_loop()

zq = Queue() # queue for communication with Zoomer thread
oq = Queue() # queue for communication with OBS messenger thread

def returnCameraIndexes():
    # checks the first 10 indexes.
    index = 0
    arr = []
    i = 10
    while i > 0:
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
        i -= 1
    return arr

def main():
    """
    Dedicated thread for grabbing video frames with VideoGet object.
    Dedicated thread for showing video frames with VideoShow object.
    Main thread serves only to pass frames between VideoGet and
    VideoShow objects/threads.
    """
    counter = 0
    frame = 1/30

    print('starting')

    switchCameraEvery = 15 # seconds
    takeCompFrameEvery = 1.0 # seconds

    obs_channel = OBSChannel(loop=loop)
    print('obs_channel thread started...')


    
    zoomer = Zoomer(obs=obs_channel).start()


    print('zoomer thread started')

    while True:
        counter += 1
        if(counter%(30*switchCameraEvery)==0):
            print(counter)
            obs_channel.chooseCamera()


        if(counter%(30*takeCompFrameEvery)==0):
            obs_channel.saveCompFrame()
            
        if obs_channel.stopped or zoomer.stopped:
            obs_channel.stop()
            zoomer.stop()
            break
        
        time.sleep(frame*.99)

main()
