#!/usr/bin/env python
import os.path
import numpy as np
import torch
import torch.nn.functional as F
import tools
import itertools
import custom_models
import yaml

with open('./../param.yaml',"r") as learningStream:
	paramLoaded = yaml.safe_load(learningStream)

savePath = paramLoaded["savePath"]
totalJoints = paramLoaded["totalJoints"]
learnErrorModel = paramLoaded["learnErrorModel"]
learntModelLoc = paramLoaded["learntModelLoc"]

eta = paramLoaded["etaCoupled"]
nb_hidden_layers = paramLoaded["layersCoupled"]
nb_hidden_neurons = paramLoaded["neuronsCoupled"]

testDataFileName = "testJointData"

meanDataFileName = "trainDataMean"
stdDataFileName = "trainDataStd"

print("> Loading the test data")

testDataFileName = os.path.join(savePath, testDataFileName + ".csv")
meanDataFileName = os.path.join(learntModelLoc, meanDataFileName + ".txt")
stdDataFileName = os.path.join(learntModelLoc, stdDataFileName + ".txt")

testData = np.genfromtxt(testDataFileName, dtype=float, delimiter=',') # np array of 7 columns with each column corresponding to that joint's torque

meanData = np.genfromtxt(meanDataFileName, dtype=float) # Contains the mean and std of the training data on which the model was trained
stdData = np.genfromtxt(stdDataFileName, dtype=float)   # Will be used to normalise the test data before making predictions

meanData = np.reshape(meanData, (-1,3*totalJoints))
stdData = np.reshape(stdData, (-1,3*totalJoints))

testDataSize = np.shape(testData)[0]

print("> Test data size: ", testDataSize)

if torch.cuda.is_available():
    device = torch.device('cuda')
else:
    device = torch.device('cpu')          

print("> Normalising the test data")

test_input = testData[:testDataSize, 0:3*totalJoints]
test_input = (test_input - meanData)/stdData

test_input = torch.from_numpy(test_input)
test_input = test_input.float()
test_input = test_input.to(device)
          
debug = True

#-----------------------------------------
print("> Loading the model")
# Loading the model

if learnErrorModel:
    modelPath = os.path.join(learntModelLoc, 'error.pt')
else:
    modelPath = os.path.join(learntModelLoc, 'torque.pt')

model = custom_models.InverseDynamicModel(nb_hidden_layers, nb_hidden_neurons).to(device)
model = torch.load(modelPath)
model.eval()

print("> Testing the model")

predTau = model(test_input) # model predicted joint torques for the test sets
predTau = predTau.cpu().data.numpy()

print("> Saving the predictions")


if learnErrorModel:
	predTauFileName = "ANN_Error_predictions_test"
else:
	predTauFileName = "ANN_Full_predictions_test"

predTauFileName = os.path.join(savePath, predTauFileName + ".csv")

np.savetxt(predTauFileName, predTau, delimiter=",")