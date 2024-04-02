from threading import Thread
import cv2
import numpy as np
import imutils
from PIL import Image
import time
from array import array
from skimage.metrics import structural_similarity as compare_ssim
from sklearn.cluster import DBSCAN
import matplotlib.image as mpimg
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
# import only system from os 
from os import system, name, path

def clear(): 
  
    # for windows 
    if name == 'nt': 
        _ = system('cls') 
  
    # for mac and linux(here, os.name is 'posix') 
    else: 
        _ = system('clear')

class Zoomer:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread. 
    """

    def __init__(self, folder='C:/paintingmusic/output', cap_dims=(3840,2160), filename='Screenshot.png',obs=False, outputDownscale=2, pollInterval=0.5, maxZoom=2.0):
        
        print('In Zoomer constructor')

        self.stopped = False
        self.obs = obs
        self.screenshot = folder+'/'+filename

        print('BP1')
        
        ss = cv2.imread(self.screenshot)
        if(ss is None):
            while ss is None: # file being written to by OBS, try again
                print('RETRYING INIT LOAD')
                time.sleep(0.11)
                ss = cv2.imread(self.screenshot)

        self.srcHeight,self.srcWidth,_ = ss.shape


        print('BP2')

        # self.newImage = cv2.resize(ss,(self.srcWidth//processDownscale,self.srcHeight//processDownscale))
        self.newImage = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)
        
        self.newImage = cv2.GaussianBlur(self.newImage,(5,5),0)

        self.prevImage = self.newImage.copy()

        print('Dimensions: ',self.srcWidth,self.srcHeight)
        # cap.set(cv2.CAP_PROP_POS_FRAMES, 37000)

        # self.processDownscale = processDownscale
        # self.outputDownscale = outputDownscale

        self.source_dims = (self.srcWidth,self.srcHeight)
        self.proc_dims =(self.srcWidth,self.srcHeight)
        self.ar = float(self.srcWidth)/float(self.srcHeight)

        self.dpos = np.array([0.5,0.5,1]) # x[0-1], y[0-1], zoom
        self.tpos = np.array([0.5,0.5,1])
        self.fpos = np.array([0.5,0.5,1])

        self.cap_dims = np.array(cap_dims)

        self.maxZoom = maxZoom
        self.pollInterval = pollInterval
        self.ssim_min = 0.75 # only frames with similarities above this limit are considered
        self.ssim_max = 0.97 # only frames with similarities below this limit are considered
        self.boxes = self.create_blank(self.proc_dims[0],self.proc_dims[1])

        patterns = '*'

        ignore_patterns = ""
        ignore_directories = True
        case_sensitive = True
        self.handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
        
        self.handler.on_modified = self.on_modified

        self.watcher = Observer()
        self.watcher.schedule(self.handler, folder, recursive=False)

    def mapr(self,value, start1, stop1, start2, stop2):
        return (value - start1) / (stop1 - start1) * (stop2 - start2) + start2

    def get_transform(self):
        size = self.cap_dims*self.fpos[2]*0.5
        position = [self.mapr(self.fpos[0],0.245,0.755,1920,0),self.mapr(self.fpos[1],0.245,0.755,1080,0)]

        return position,size

    def start(self):    
        Thread(target=self.get, args=()).start()
        return self

    def on_modified(self,event):
        
        last4 = event.src_path[-4:]
        last12 = event.src_path[-12:]
        if(last4=='.png'):
            ss = cv2.imread(self.screenshot)

            if(ss is None):
                while ss is None: # file being written to by OBS, try again
                    fs = path.getsize(event.src_path)

                    # print('RETRYING LOAD {}'.format(fs))
                    time.sleep(.05)
                    try:
                        ss = cv2.imread(event.src_path)
                    except:
                        _ = False

        
            # self.newImage = cv2.resize(ss,(self.srcWidth//self.processDownscale,self.srcHeight//self.processDownscale))
            self.newImage = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)
            self.newImage = cv2.GaussianBlur(self.newImage,(5,5),0)
            # self.newImage = cv2.GaussianBlur(self.newImage,(1,1),0)
            self.compare()

        if last12=='sendtoai.txt':   
            f = open(event.src_path, "r")
            q = f.read()
            f.close()
            if(q == 'YES'):
                print('Received send-to-AI request from Stream Deck')
                # send to ai request
                self.obs.sendToAI()
                # clear request
                f = open("C:/paintingmusic/scripts/sendtoai.txt", "w")
                q = f.write('NO')
                f.close()


    def create_blank(self,width, height, rgb_color=(0, 0, 0)):
        """Create new image(numpy array) filled with certain color in RGB"""
        # Create black blank image
        image = np.zeros((height, width, 3), np.uint8)
        # Since OpenCV uses BGR, convert the color first
        color = list((rgb_color))
        # Fill image with color
        image[:] = color
        return image

    def halve(self,src,factor=2):
        return src[::factor, ::factor, :]

    def get(self):
        self.watcher.start()
        try:
            while True:
                time.sleep(self.pollInterval)
                # clear()
        except KeyboardInterrupt:
            self.watcher.stop()
            self.watcher.join()
           
    def bb(self,pos,dims):

        # return bounding box of zoomed and cropped window at given dimensions

        if(pos[2]<1):
            pos[2]=1
        if(pos[2]>2):
            pos[2]=2

        # draw the zoomed bounding box on the preview image
        bbCenter = [pos[0]*dims[0],pos[1]*dims[1]]

        minY = dims[1]/(2*pos[2])
        maxY = dims[1] - minY
        minX = dims[0]/(2*pos[2])
        maxX = dims[0] - minX




        if(bbCenter[0]<minX):
            bbCenter[0] = minX
        if(bbCenter[0]>maxX):
            bbCenter[0] = maxX
        if(bbCenter[1]<minY):
            bbCenter[1] = minY
        if(bbCenter[1]>maxY):
            bbCenter[1] = maxY

        bbDims = (dims[0]/pos[2],dims[1]/pos[2])

        bbTopleft = (int(bbCenter[0]-bbDims[0]/2),int(bbCenter[1]-bbDims[1]/2))
        bbBottomright = (int(bbCenter[0]+bbDims[0]/2),int(bbCenter[1]+bbDims[1]/2))

        return bbTopleft,bbBottomright


    def compare(self):
        # print(self.newImage.shape,self.prevImage.shape)
        (score, diff) = compare_ssim(self.newImage, self.prevImage, full=True)
        diff = (diff * 255).astype("uint8")
        # print("SSIM: {}".format(score))
        
        xcumul = 0
        ycumul = 0
        gcount = 0
        if(score>=self.ssim_min and score<=self.ssim_max):
            # threshold the difference image, followed by finding contours to
            # obtain the regions of the two input images that differ
            retval,thresh = cv2.threshold(diff, 127, 255,
                cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            

            # loop over the contours
            b = 0

            good_contours = []
            raw = []

            for c in cnts[:12]:
                # compute the bounding box of the contour and then draw the
                # bounding box on both input images to represent where the two
                # images difference
                (x, y, w, h) = cv2.boundingRect(c)
                if(w<self.proc_dims[0]*0.5 and h<self.proc_dims[1]*0.5):
 
                        
                    # print(w,h)
                    
                    gcount += 1
                    good_contours.append(c)
                    raw.append((x,y))
                

                b += 1
            
            if(gcount>2):

                self.boxes = self.create_blank(self.proc_dims[0],self.proc_dims[1])
                pcount = 0

                # isolate and exclude outliers
                model = DBSCAN(eps=20,min_samples=3).fit(raw)
                # print(model)
                # print((model.labels_))
                i = 0
                for c in good_contours:
                    (x, y, w, h) = cv2.boundingRect(c)
                    if(model.labels_[i]==-1):
                        color=(0,0,255)
                    elif(model.labels_[i]==0):
                        
                        # additional filtering: ignore margins
                        if(
                            x>self.proc_dims[0]*0.15 and
                            x<self.proc_dims[0]*0.9 and
                            y>self.proc_dims[1]*0.3 and
                            y<self.proc_dims[1]*0.66
                        ):
                            # additional filtering: ignore hand area of table (bottom right triangle)
                            if(y<=(self.proc_dims[0]-x)*1):

                                # prime group
                                xcumul += x
                                ycumul += y
                                pcount += 1
                                color=(0,255,0)
                            else:
                                # point is in hand area; ignore but show as yellow in overlay
                                color=(0,255,255)
                        else:
                            # point is in margins; ignore but show as cyan in overlay
                            color=(255,255,0)

                    else:
                        color=(255,0,0)
                    cv2.rectangle(self.boxes, (x,y), (x + w, y + h), color, 1)
                    i+=1


                if(pcount>0):
                    xcumul /= pcount # average x
                    ycumul /= pcount # average y

                    cv2.circle(self.boxes, (int(xcumul),int(ycumul)), 5, (0,255,0),-1)

                    # print('Barycentre: '+str(xcumul)+', '+str(ycumul))

                    self.tpos[0] = xcumul/self.proc_dims[0]
                    self.tpos[1] = ycumul/self.proc_dims[1]
                    self.tpos[2] = 2

                else:
                    # print('No non-outlying contours')
                    self.boxes[0:5][0:5] = (255,0,255)
                    
            else:
                # contour count of 3 or lower. Good/bad?
                # print('Skipping for low gcount: ',gcount)
                self.boxes = self.create_blank(self.proc_dims[0],self.proc_dims[1])
                self.boxes[0:5][0:5] = (255,255,0)
                
                self.tpos[:] = self.dpos[:] # reset


        else:
            
            
            if(score<self.ssim_min):
                # print('skipping comp frame because images too dissimilar. Resetting')
                self.boxes = self.create_blank(self.proc_dims[0],self.proc_dims[1])
                self.boxes[0:5][0:5] = (0,255,255)
                self.tpos[:] = self.dpos[:] # reset
            #else:
            #    print('skipping comp frame because images too similar. NOT resetting')
        
        self.fpos = self.tpos.copy()

        if(self.fpos[2]<1.005):
            self.fpos[2]=1.005
        if(self.fpos[2]>self.maxZoom):
            self.fpos[2]=self.maxZoom

        minY = 1./(2.*self.fpos[2])
        maxY = 1.-minY
        maxX = maxY
        minX = minY


        if(self.fpos[0]<minX): self.fpos[0]=minX
        if(self.fpos[0]>maxX): self.fpos[0]=maxX
        if(self.fpos[1]<minY): self.fpos[1]=minY
        if(self.fpos[1]>maxY): self.fpos[1]=maxY

        self.prevImage = self.newImage.copy()

        bbTopleft,bbBottomright = self.bb(self.fpos,self.proc_dims)

        zbox = self.create_blank(self.proc_dims[0],self.proc_dims[1])

        cv2.rectangle(zbox, bbTopleft, bbBottomright, (127,0,255), 1)

        cv2.imshow('preview',cv2.add(cv2.add(zbox,cv2.cvtColor(self.newImage,cv2.COLOR_GRAY2BGR)),self.boxes))
        
        self.position, self.size = self.get_transform()

        #x y w h
        f = open("./position.txt", "w")
        f.write("{}\n{}\n{}\n{}".format(self.position[0],self.position[1],self.size[0],self.size[1]))
        f.close()


        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit()

    def stop(self):
        self.stopped = True