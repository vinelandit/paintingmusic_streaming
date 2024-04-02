import simpleobsws
import asyncio
import random 

class OBSChannel:
    """
    Class that continuously gets frames from a VideoCapture object
    with a dedicated thread.
    """

    def __init__(self, host='localhost',port=4455,password='p9QLCp2KLpIqEcG4', loop=False, queue=False):
        # self.ws = simpleobsws.obsws(host=host, port=port, password=password, loop=loop) # Every possible argument has been passed, but none are required. See lib code for defaults.
        self.ws = simpleobsws.WebSocketClient(url='ws://'+host+':'+str(port), password=password)
        self.loop = loop
        self.loop.run_until_complete(self.connect())

        self.cameras = ['Side','Closeup','Overhead']
        self.curcamid = 0
        self.messageCounter = 1
        self.stopped = False

    async def connect(self):
        await self.ws.connect() # Make the connection to OBS-Websocket
        await self.ws.wait_until_identified()
        print("Connected and identified.")

    async def disconnect(self):
        await self.ws.disconnect()

    async def switch_camera(self,camname):

        req = simpleobsws.Request('GetSceneItemId', {
        'sceneName':'Auto',
        'sourceName': camname
        })
        result = await self.ws.call(req) # Make a request with the given data
        print(result)
        camid = result.responseData['sceneItemId']
        self.messageCounter += 1


        req = simpleobsws.Request('SetSceneItemEnabled', {
        'sceneName':'Auto',
        'sceneItemId': camid,
        'sceneItemEnabled': True
        })
        print(req)
        result = await self.ws.call(req) # Make a request with the given data
        print(result)
        self.messageCounter += 1

    async def send_to_ai(self):

        req = simpleobsws.Request('SaveSourceScreenshot', {
        'sourceName':'Overhead',
        'imageFilePath':'C:/paintingmusic/output/toai.png',
        'imageFormat': 'png'
        })

        result = await self.ws.call(req) # Make a request with the given data
        print(result)
        self.messageCounter += 1

    async def save_comp_frame(self):
        req = simpleobsws.Request('SaveSourceScreenshot', {
        'sourceName':'Closeup',
        'imageFilePath':'C:/paintingmusic/output/Screenshot.png',
        'imageFormat': 'png',
        'imageWidth':320,
        'imageHeight':180,
        
        })
        print(req)
        result = await self.ws.call(req) # Make a request with the given data
        print(result)
        
        self.messageCounter += 1

    async def update_transform(self,position):
        position[0] -= 0.5
        position[1] -= 0.5
        position[0] *= 1920
        position[1] *= 1080

        pos = {'x':position[0],'y':position[1]}
        siz = {'x':position[2],'y':position[2]}

        req = simpleobsws.Request('GetSceneItemId', {
        'sceneName':'Auto',
        'sourceName': 'Closeup'
        })
        result = await self.ws.call(req) # Make a request with the given data
        print(result)
        camid = result.responseData['sceneItemId']
        self.messageCounter += 1


        req = simpleobsws.Request('SetSceneItemTransform', {
            'sceneName':'Auto',
            'sceneItemId':camid,
            'sceneItemTransform': {
                    'pos': pos,
                    'scale': siz
                }
            })

        result = await self.ws.call(req) # Make a request with the given data
        print(result)
        self.messageCounter += 1

    def chooseCamera(self):
        availablecids = []
        for i in range(0,len(self.cameras)):
            if(i!=self.curcamid):
                availablecids.append(i)


        # print('Len acids: '+str(len(availablecids)))
        if(len(availablecids)>0):
            newcid = availablecids[random.randrange(len(availablecids))]
            newcname = self.cameras[newcid]
            print('Auto-switching to {} camera'.format(newcname))
            self.curcamid = newcid
            self.loop.run_until_complete(self.switch_camera(newcname))

    def updateTransform(self,pos):
        self.loop.run_until_complete(self.update_transform(pos))

    def saveCompFrame(self):
        self.loop.run_until_complete(self.save_comp_frame())

    def sendToAI(self):
        self.loop.run_until_complete(self.send_to_ai())