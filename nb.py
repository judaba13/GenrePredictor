'''
Created on Nov 13, 2014

@author: Daniel Nam dwn28
'''

import math 
from Datapoint import Datapoint

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
        
    n = len(trainlabel)
    npos = 0
    nneg = 0
    for label in trainlabel:
        if label == 1: npos = npos+1
        else: nneg = nneg+1
    posindex = find(trainlabel,1)
    negindex = find(trainlabel,-1)
    lpos = 0
    lneg = 0
    v = 0
    wpos = []
    wneg = []
    for idx in posindex:
        featurespace = trainfeature(idx)
        lpos = sum(featurespace) + lpos
        v = max([v,len(featurespace)])
        for k in range(len(featurespace)):
            if k+1 <= len(wpos):
                wpos[k] = wpos[k] + featurespace[k]
            else:
                wpos[k] = featurespace[k]
                
    for idx in negindex:
        featurespace = trainfeature(idx)
        lneg = sum(featurespace) + lneg
        v = max([v,len(featurespace)])
        for k in range(len(featurespace)):
            if k+1 <= len(wneg):
                wneg[k] = wneg[k] + featurespace[k]
            else:
                wneg[k] = featurespace[k]
    
    PYpos = npos/n
    PYneg = nneg/n
    PWYpos = matdiv([w+1 for w in wpos],[l+v for l in lpos])
    PWYneg = matdiv([w+1 for w in wneg],[l+v for l in lneg])
    classification = [0]*len(testfeature)
    for i in range(len(testfeature)):
        featurespace = testfeature[i]
        probpos = nbprob(PWYpos,PYpos,featurespace)
        probneg = nbprob(PWYneg,PYneg,featurespace)
        if probpos >= probneg:
            classification[i] = 1
        else: classification[i] = -1
    
    testAccuracy = accuracy(classification,testlabel)
    print "Accuracy: ", testAccuracy
        
    
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
