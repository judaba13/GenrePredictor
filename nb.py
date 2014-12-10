'''
Created on Nov 13, 2014

@author: Daniel Nam dwn28
'''

import math 
import pickle
from Artistdata import *


def nb(traindata, testdata):
    
    trainlabel = []
    testlabel = []
    trainfeature = []
    testfeature = []

# reading the train data
    trainfile = open('traindata.txt','a')
    for d in traindata:
        if d.label==0:
            trainfile.write(str(-1))
        else:
            trainfile.write(str(d.label))
        trainfile.write(' ')
        featuremat = []
        count = 1
        for feature in d:
            trainfile.write(str(count))
            trainfile.write(':')
            trainfile.write(str(d[feature]))
            trainfile.write(' ')
            count = count + 1
            featuremat.append(d[feature])
        trainfeature.append(featuremat)
        trainlabel.append(d.label)
        trainfile.write('\n')
    trainfile.close()

# reading the test data
    testfile = open('testdata.txt','a')
    for d in testdata:
        if d.label==0:
            testfile.write(-1)
        else:
            testfile.write(str(d.label))
        testfile.write(' ')
        featuremat = []
        count = 1
        for feature in d:
            testfile.write(str(count))
            testfile.write(':')
            testfile.write(str(d[feature]))
            testfile.write(' ')
            count = count+1
            featuremat.append(d[feature])
        testfile.write('\n')
        testfeature.append(featuremat)
        testlabel.append(d.label)
    testfile.close()

# running Naive Bayes
    vspace = [[]]
    for j in range(len(trainfeature[0])):
                vspace.append([])
    for idx in range(len(trainfeature)):
        testdata = trainfeature[idx]
        for j in range(len(testdata)):
            vspace[j].append(testdata[j])
    v = []
    for feature in vspace:
        v.append(len(set(feature)))
    print trainlabel.count(1),' / ',len(trainlabel)
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
                PXY = float(featurepool.count(feature)+1)/(len(featurepool)+v[j])
                nbprob = nbprob * PXY
            # storing the probability of each label cases
            probs.append(nbprob)
        # determine the label with maximum probability and add to results
        maxprob = max(probs)
        results.append(labels[probs.index(maxprob)])
    # result contains the max probability label for each test case
    print 'acc: ', accuracy(results,testlabel)
    print 'pre: ', precision(results,testlabel)
    return results


def accuracy(result, data):
    # calculates accuracy
    match = 0
    for i in range(len(result)):
        if result[i]-data[i]==0:
            match = match+1
    return float(match)/len(result)

def precision(result, data):
    # calculates precision
    match = 0
    for i in range(len(result)):
        if result[i]==1 and data[i]==1:
            match = match+1
    return float(match)/result.count(1)

def find(mat,element):
    # finds all index of given element in the matrix mat
    idx = []
    for i in range(len(mat)):
        if mat[i]==element:
            idx.append(i)
    return idx

if __name__ == '__main__':
    train_file = open('train.pkl', 'rb')
    test_file = open('test.pkl', 'rb')
    traindata = pickle.load(train_file)
    testdata = pickle.load(test_file)
    train_file.close()
    test_file.close()

    nb(traindata,testdata)
