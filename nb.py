'''
Created on Nov 13, 2014

@author: Daniel Nam dwn28
'''

import math 
# from Datapoint import Datapoint
import pickle
from Artistdata import *


def nb(traindata, testdata):
    
    trainlabel = []
    testlabel = []
    trainfeature = []
    testfeature = []
    for d in traindata:
        featuremat = []
        for feature in d:
            featuremat.append(d[feature])
        trainfeature.append(featuremat)
#         TODO:
#         trainlabel
        trainlabel.append(d.label)

    for d in testdata:
#         TODO: add test label
        featuremat = []
        for feature in d:
            featuremat.append(d[feature])
        testfeature.append(featuremat)
        testlabel.append(d.label)

    labels = list(set(trainlabel))
    labelindex = []
    for i in range(len(labels)):
        label = labels[i]
        labelindex.append(find(trainlabel,label))
    results = []
    count = 1
    for testcase in testfeature:
        print 'testcase',count
        count = count + 1
        # getting a result for a single test case. If there is only one test case, 
        # it will only run once.
        probs = []
        for label in labels:
            # find probaility of each label and store the result 
            nlabel = len(labelindex[labels.index(label)])
            PY = float(nlabel)/len(trainlabel)
            index = labelindex[labels.index(label)]
            index = index[0:30]
            nbprob = PY
            newfeatures = [[]]
            # change the direction of the feature matrix of the specific label case
            for j in range(len(testcase)):
                newfeatures.append([])
            for idx in index:
                testdata = trainfeature[idx]
                for j in range(len(testdata)):
                    newfeatures[j].append(testdata[j])
            # find PXY for each feature and mutiply to the final probability 
            # to find the prob of each label
            for j in range(len(testcase)):
                feature = testcase[j]
                featurepool = newfeatures[j]
                # print featurepool
                PXY = float(featurepool.count(feature)+1)/(len(featurepool)+len(set(featurepool)))
                nbprob = nbprob * PXY
            # storing the probability of each label cases
            probs.append(nbprob)
        # determine the label with maximum probability and add to results
        maxprob = max(probs)
        results.append(labels[probs.index(maxprob)])
    # result contains the max probability label for each test case
    print 'acc: ', accuracy(results,testlabel)
    return results

def accuracy(result, data):
    match = 0
    for i in range(len(result)):
        if result[i]-data[i]==0:
            match = match+1
    return float(match)/len(result)

def find(mat,element):
    idx = []
    for i in range(len(mat)):
        if mat[i]==element:
            idx.append(i)
    return idx

if __name__ == '__main__':
    pkl_file = open('data.pkl', 'rb')
    data = pickle.load(pkl_file)
    pkl_file.close()

    nb(data,data)
