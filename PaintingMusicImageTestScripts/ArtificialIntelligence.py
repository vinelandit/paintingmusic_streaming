"""
This script should contain all training and deployment of models
"""
# Libraries
import pickle
from minisom import MiniSom
from sklearn.preprocessing import MinMaxScaler

def SOM(FeatureRow):
    # Specify folder containing the training data set and 
    TrainingFile = './TrainingSet.dat'
    SOMFile = './SOM.p'
    # Load training set
    TrainingSet = pickle.load(open(TrainingFile, "rb"))
    # Feature scale
    sc = MinMaxScaler(feature_range=(0, 1))
    TrainingSet = sc.fit_transform(TrainingSet)
    # Feature scale the passed in data
    FeatureRow = sc.transform(FeatureRow)
    # Load up the SOM
    with open(SOMFile, 'rb') as infile:
        som = pickle.load(infile)
    
    # Pass the feature row into the SOM nd return the winning node
    return som.winner(FeatureRow)


