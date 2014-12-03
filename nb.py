'''
Created on Nov 13, 2014

@author: Daniel Nam dwn28
'''

import math 
from Artistdata import *

def nb(traindata, testdata):
    
    trainlabel = []
    testlabel = []
    trainfeature = []
    testfeature = []
    for d in traindata:
        featuremat = []
        for feature in d:
            featuremat.append(feature)
        trainfeature.append(featuremat)
#         TODO:
#         trainlabel
        trainlabel.append(d.familiarity)
        
    for d in testdata:
#         TODO: add test label
        featuremat = []
        for feature in d:
            featuremat.append(feature)
        testfeature.append(featuremat)
        testlabel.append(d.familiarity)

    labels = list(set(trainlabel))
    labelindex = []
    for label in labels:
        labelindex.append(find(trainlabel,label))

    results = []
    for testcase in testfeature:
        # getting a result for a single test case. If there is only one test case, it will only run once.
        probs = []
        for label in labels:
            # find probaility of each label and store the result 
            nlabel = len(labelindex[labels.index(label)])
            PY = nlabel/len(trainlabel)
            index = labelindex[labels.index(label)]
            nbprob = PY
            newfeatures = [[]]
            # change the direction of the feature matrix of the specific label case
            for i in range(len(testcase)):
                newfeatures.append([])
            for idx in index:
                testdata = trainfeature[idx]
                for i in range(len(testdata)):
                    newfeatures[i].append(testdata[i])
            # find PXY for each feature and mutiply to the final probability to find the prob of each label
            for i in range(len(testcase)):
                feature = testcase[i]
                featurepool = newfeatures[i]
                PXY = (featurepool.count(feature)+1)/(len(featurepool)+len(set(featurepool)))
                nbprob = nbprob * PXY
            # storing the probability of each label cases
            probs.append(nbprob)
        # determine the label with maximum probability and add to results
        maxprob = max(probs)
        results.append(labels[probs.index(maxprob)])
    # result contains the max probability label for each test case
    print accuracy(results,testlabel)
    return results

def accuracy(result, data):
    match = 0
    for i in range(len(result)):
        if result[i]==data[i]:
            match = match+1
    return match/len(result)

def find(mat,element):
    idx = []
    for i in range(len(mat)):
        if mat[i]==element:
            idx.append(i)
    return idx