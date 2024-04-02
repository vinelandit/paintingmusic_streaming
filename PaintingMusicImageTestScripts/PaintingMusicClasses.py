"""
This contains Painting Music Classes
"""
# Import Libraries
import ArtificialIntelligence as AI
import FeatureExtraction as FE

class PaintedObject():
    def __init__(self, Img):
        self.Img = Img
        self.Features = FE.FeatureExtraction(self.Img)
        self.WinningNode = AI.SOM(self.Features)