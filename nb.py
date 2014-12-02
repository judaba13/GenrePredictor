'''
Created on Nov 13, 2014

@author: Daniel Nam dwn28
'''

import math 
from Datapoint import Datapoint
import numpy as np

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
        trainlabel.append(d.label)
        
    for d in testdata:
#         TODO: add test label
        featuremat = []
        for feature in d:
            featuremat.append(feature)
        testfeature.append(featuremat)
        testlabel.append(d.label)

    labels = list(set(trainlabel))
    labelindex = []
    for label in labels:
        labelindex.append(find(trainlabel,label))

    results = []
    for testcase in testfeature:
        probs = []
        for label in labels:
            nlabel = len(labelindex[labels.index(label)])
            PY = nlabel/len(trainlabel)
            index = labelindex(labels.index(label))
            nbprob = PY
            newfeatures = [[]*len(testcase)]
            for idx in index:
                testdata = trainfeature[idx]
                for i in range(len(testdata)):
                    newfeatures[i].append(testdata[i])
            for i in range(len(testcase)):
                feature = testcase[i]
                featurepool = newfeatures[i]
                PXY = (featurepool.count(feature)+1)/(len(featurepool)+len(set(featurepool)))
                nbprob = nbprob * PXY
            probs.append(nbprob)
        maxprob = max(probs)
        results.append(labels(probs.index(maxprob)))
    return results




        
    
def accuracy(result, data):
    match = 0
    for i in range(len(result)):
        if result[i]==data[i]:
            match = match+1
    return match/len(result)

def nbprob(pwy,py,feature):
    problist = []
    for i in range(len(feature)):
        problist.append(math.log(math.pow(pwy[i],feature[i])))
    return sum(problist + math.log(py))
    
def matdiv(mat1,mat2):
    result = []
    for i in range(len(mat1)):
        result.append(mat1[i]/mat2[i])
    return result

def find(mat,element):
    idx = []
    for i in range(len(mat)):
        if mat(i)==element:
            idx.append(i)
    return idx
    
    
# if __name__ == '__main__':
#     nb(data)
#     pass
