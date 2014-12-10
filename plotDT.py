from matplotlib import pyplot as plt
from dt import *


trainData, testData = getData()

def prune(i, data):
    tree = trainDT(trainData)
    tree.postPrune(tree.root, i)
    a, p = tree.test(tree, data)
    return a, p

depths = range(2, 33)
testAccuracies = []
testPrecisions = []
trainAccuracies = []
trainPrecisions = []

for i in range(2, 33):
    a, p = prune(i, testData)
    testAccuracies.append(a)
    testPrecisions.append(p)
    atr, ptr = prune(i, trainData)
    trainAccuracies.append(atr)
    trainPrecisions.append(ptr)

#print str(testAccuracies)
#print str(testPrecisions)
#print str(trainAccuracies)
#print str(trainPrecisions)

plt.figure()
plt.title("Test Accuracy vs Depth")
plt.xlabel("Max Depth")
plt.ylabel("Test Accuracy")
plt.plot(depths, testAccuracies, ".")
plt.savefig("DtTestAccuracy.png")

plt.figure()
plt.title("Test Precision vs Depth")
plt.xlabel("Max Depth")
plt.ylabel("Test Precision")
plt.plot(depths, testPrecisions, ".")
plt.savefig("DtTestPrecision.png")

plt.figure()
plt.title("Training Accuracy vs Depth")
plt.xlabel("Max Depth")
plt.ylabel("Training Accuracy")
plt.plot(depths, trainAccuracies, ".")
plt.savefig("DtTrainAccuracy.png")

plt.figure()
plt.title("Training Precision vs Depth")
plt.xlabel("Max Depth")
plt.ylabel("Training Precision")
plt.plot(depths, trainPrecisions, ".")
plt.savefig("DtTrainPrecision.png")

plt.figure()
plt.title("Training and Test Accuracy vs Depth")
plt.xlabel("Max Depth")
plt.ylabel("Accuracy")
plt.plot(depths, trainAccuracies, "x", label="on training data")
plt.plot(depths, testAccuracies, ".", label="on test data")
plt.legend()
plt.savefig("DtTrainAndTestAccuracy.png")

plt.figure()
plt.title("Training and Test Precision vs Depth")
plt.xlabel("Max Depth")
plt.ylabel("Precision")
plt.plot(depths, trainPrecisions, "x", label="on training data")
plt.plot(depths, testPrecisions, ".", label="on test data")
plt.legend()
plt.savefig("DtTrainAndTestPrecision.png")
