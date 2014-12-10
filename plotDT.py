'''
CS4780 Final Project
Post Pruning and Cross Validation
@author: Kelsey Duncan ked83
'''
from matplotlib import pyplot as plt
from dt import *
import random

#get data
trainData, testData = getData()

depths = range(2, 33)
testAccuracies = []
testPrecisions = []
trainAccuracies = []
trainPrecisions = []

#train a tree on 'trData' and prune it to depth 'i' then test on tsData
#return accuracy and precision
def prune(i, trData, tsData):
    tree = trainDT(trData)
    tree.postPrune(tree.root, i)
    a, p = tree.test(tree, tsData)
    return a, p

#get test and train accuracies and precisions for each depth
def fillArrays():
    for i in range(2, 33):
        a, p = prune(i, trainData, testData)
        testAccuracies.append(a)
        testPrecisions.append(p)
        atr, ptr = prune(i, trainData, trainData)
        trainAccuracies.append(atr)
        trainPrecisions.append(ptr)

#print str(testAccuracies)
#print str(testPrecisions)
#print str(trainAccuracies)
#print str(trainPrecisions)

#plot depth vs 'yVals'
def pltG(title, yVals):
    plt.figure()
    plt.title(title + " vs Depth")
    plt.xlabel("Max Depth")
    plt.ylabel(title)
    plt.plot(depths, yVals, ".")
    plt.savefig("DT "+ title + ".png")

def plotGraphs():
    pltG("Test Accuracy", testAccuracies)
    pltG("Test Precision", testPrecisions)
    pltG("Training Accuracy", trainAccuracies)
    pltG("Training Precision", trainPrecisions)
    
    plt.figure()
    plt.title("Training and Test Accuracy vs Depth")
    plt.xlabel("Max Depth")
    plt.ylabel("Accuracy")
    plt.plot(depths, trainAccuracies, "x", label="on training data")
    plt.plot(depths, testAccuracies, ".", label="on test data")
    plt.legend()
    plt.savefig("DT Train & Test Accuracy.png")
    
    plt.figure()
    plt.title("Training and Test Precision vs Depth")
    plt.xlabel("Max Depth")
    plt.ylabel("Precision")
    plt.plot(depths, trainPrecisions, "x", label="on training data")
    plt.plot(depths, testPrecisions, ".", label="on test data")
    plt.legend()
    plt.savefig("DT Train & Test Precision.png")

#plot cross validation accuracies and precisions
def plotCV(results, f, title):
    x = [results[r][2] for r in results if results[r][0] != None]
    y = [results[r][0] for r in results if results[r][0] != None]
    plt.figure()
    plt.title(title+ ": " + str(f) + "-fold CV Accuracy vs d")
    plt.xlabel("d")
    plt.ylabel("average accuracy")
    plt.plot(x, y, ".")
    plt.savefig(title + "CV Accuracy.png")
    x = [results[r][2] for r in results if results[r][1] != None]
    y = [results[r][1] for r in results if results[r][1] != None]
    plt.figure()
    plt.title(title+ ": " + str(f) + "-fold CV Precision vs d")
    plt.xlabel("d")
    plt.ylabel("average precision")
    plt.plot(x, y, ".")
    plt.savefig(title + "CV Precision.png")

#get accuracy and precision for depth 'd' training on trainData and testing on testData
def test(trainData, testData, d):
    a, p = prune(d, trainData, testData)
    result = []
    result.append(a)
    result.append(p)
    return result

#cross validate with 'f' folds
def crossValidate(trainD, testD, depths, f, title):
    random.shuffle(trainD)
    size = float(len(trainD))/f
    results = {d:[0., 0.] for d in depths}
    counts = {d:[0, 0] for d in depths}
    for i in range(f):
        for d in depths:
            result = test(trainD[0:int(i*size)]+trainD[int((i+1)*size):], trainD[int(i*size):int((i+1)*size)], d)
            for j in range(2):
                if result[j] != None:
                    results[d][j] += result[j]
                    counts[d][j] += 1
    for d in depths:
        for j in range(2):
            if counts[d][j] > 0:
                results[d][j] /= f
            else:
                results[d][j] = None
        results[d].append(d)
    d = max(results, key=lambda r: results[r][0])
    bestAccuracy = results[d]
    print "Best Accuracy: ", bestAccuracy
    d = max(results, key=lambda r: results[r][1])
    bestPrecision = results[d]
    print "Best Precision:", bestPrecision
    plotCV(results, f, title)
    return (test(trainD, testD, bestAccuracy[2]), test(trainD, testD, bestPrecision[2]))

def main():
    print "filling arrays"
    fillArrays()
    print "plotting graphs"
    plotGraphs()
    print "Cross Validating.."
    bestA, bestP = crossValidate(trainData, testData, depths, 7, "DT ")
    print "Testing on best depth for accuracy.. accuracy = " + str(bestA[0]) + " precision = " + str(bestA[1])
    print "Testing on best depth for precision.. accuracy = " + str(bestP[0]) + " precision = " + str(bestP[1])

main()