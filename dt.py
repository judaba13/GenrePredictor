import math
import pickle
from Artistdata import *

class ID3(object):

    def __init__(self, root, nots=0, hots=0, total=0, nodes=0, leaves=0, depth=0, realBins=10, yearBinSize=5, yearStart=1920):
        self.hots = hots
        self.nots = nots
        self.realBins = realBins
        self.yearBinSize = yearBinSize
        self.yearStart = yearStart
        self.total = total
        self.nodes = nodes
        self.leaves = leaves
        self.depth = depth
        self.root = root

    def setNums(self, data):
        numHots = 0
        numNots = 0
        for a in data:
            if(a.label == -1):
                numNots+= 1
            if(a.label == 1):
                numHots+= 1
        self.hots = numHots
        self.nots = numNots
        self.total = float(len(data))
    
    def getNotsAndHots(self, data):
        nots = 0
        hots = 0
        for a in data:
            if(a.label == -1):
                nots+= 1
            if(a.label == 1):
                hots+= 1
        return (nots, hots)
    
    def entropy(self, nots, hots):
        if nots is None:
            nots = self.nots
        if hots is None:
            hots = self.hots
        total = nots + hots
        if(total < 1 or nots < 1 or hots < 1):
            return 0
        d = -(float(nots)/float(total))*(math.log(float(nots)/float(total))/math.log(float(2.0))) - (float(hots)/float(total))*(math.log(float(hots)/float(total))/math.log(float(2.0)))
        return d
    
    #split data on condition feature is true or false
    def splitBinary(self, feature, data):
        subsetTrue = []
        subsetFalse = []
        for a in data:
            if(a[feature] == 1):
                subsetTrue.append(a)
            elif(a[feature] == 0):
                subsetFalse.append(a)
        return (subsetTrue, subsetFalse)
    
    def splitRealBuckets(self, feature, data):
        childrenSubsets = []
        delta = float(1)/(float(self.realBins))
        for i in range(0, self.realBins):
            childrenSubsets.append([])
            for a in data:
                if a[feature] >= (i)*delta and a[feature] < (i+1)*delta:
                    childrenSubsets[i].append(a)
        return childrenSubsets
    
    def splitYearBuckets(self, feature, data):
        childrenSubsets = []
        delta = self.yearBinSize
        start = self.yearStart
        end = 2011
        y = start
        i = 0
        while y <= end:
            childrenSubsets.append([])
            for a in data:
                if a[feature] >= y and a[feature] < y+delta:
                    childrenSubsets[i].append(a)
            y += delta
            i += 1
        return childrenSubsets
    
    def calculateGain(self, entropy, childrenSubsets, numTotal):
        gain = entropy
        for s in childrenSubsets:
            subsetNots, subsetHots = self.getNotsAndHots(s)
            sEntropy = self.entropy(subsetNots, subsetHots)
            gain -= (float(len(s))/float(numTotal))*sEntropy
        return gain
    
    def informationGain(self, feature, data):
        numNots, numHots = self.getNotsAndHots(data)
        numTotal = len(data)
        entropy = self.entropy(numNots, numHots)
        if feature[0:2] == "b_":
            subsetTrue, subsetFalse = self.splitBinary(feature, data)
            subsetTNots, subsetTHots = self.getNotsAndHots(subsetTrue)
            subsetTEntropy = self.entropy(subsetTNots, subsetTHots)
            subsetFNots = numNots - subsetTNots
            subsetFHots = numHots - subsetTHots
            subsetFEntropy = self.entropy(subsetFNots, subsetFHots)
            gain = entropy - (len(subsetTrue)/numTotal)*subsetTEntropy - (len(subsetFalse)/numTotal)*subsetFEntropy
        elif feature[0:2] == "y_":
            childrenSubsets = self.splitYearBuckets(feature, data)
            gain = self.calculateGain(entropy, childrenSubsets, numTotal)
        else:
            childrenSubsets = self.splitRealBuckets(feature, data)
            gain = self.calculateGain(entropy, childrenSubsets, numTotal)
        return gain
    
    def getMaxF(self,info):
        maxV = float(-9999999)
        maxF = ""
        for k, v in info.items():
            if v > maxV:
                maxF = k
                maxV = v
        return maxF, maxV
    
    #find max gain of all features putting features and gains into a dictionary
    def findBestGain(self, data, featsAndGain):
        infoGain = 0.0
        for feature in data[0].keys():
            infoGain = self.informationGain(feature, data)
            featsAndGain[feature] = infoGain
        return self.getMaxF(featsAndGain)
    
    def runID3(self, data):
        self.setNums(data)
        if(self.entropy(self.nots, self.hots) == 0):
            value = 1 if (self.nots == 0) else -1;
            self.leaves+= 1
            self.nodes+= 1
            return Node(value, None, None, "", int(self.nots), int(self.hots))
        
        (f, v) = self.findBestGain(data, {})
        #print "best gain feature: (" + f + ") value: " + str(v)
        node = Node()
        if(v > 0):
            node = Node(0, None, None, f, int(self.nots), int(self.hots))
            self.nodes+= 1
            if f[0:2] == "b_":
                subsetTrue, subsetFalse = self.splitBinary(f, data)
                node.left = self.runID3(subsetFalse)
                node.right = self.runID3(subsetTrue)
            elif f[0:2] == "y_":
                childrenSubsets = self.splitYearBuckets(f, data)
                childrenNodes = []
                for s in childrenSubsets:
                    n = self.runID3(s)
                    childrenNodes.append(n)
                node.children = childrenNodes
            else:
                childrenSubsets = self.splitRealBuckets(f, data)
                childrenNodes = []
                for s in childrenSubsets:
                    n = self.runID3(s)
                    childrenNodes.append(n)
                node.children = childrenNodes
        else:
            value = -1 if (self.nots >= self.hots) else 1
            node = Node(value, None, None, "", int(self.nots), int(self.hots))
        return node
    
    def getValue(self, node, a):
        if(not(node.value == 0)):
            return node.value
        else:
            if node.feature[0:2] == "b_":
                if a[node.feature] == 0:
                    return self.getValue(node.left, a)
                else:
                    return self.getValue(node.right, a)
            elif node.feature[0:2] == "y_":
                y = self.yearStart
                delta = self.yearBinSize
                i = 0
                while y <= 2011:
                    if a[node.feature] >= y and a[node.feature] < y+delta:
                        return self.getValue(node.children[i], a)
                    y += delta
                    i += 1
            else:
                delta = float(1)/(float(self.realBins))
                for i in range(0, self.realBins):
                    if node.feature in a.keys():
                        if a[node.feature] >= (i)*delta and a[node.feature] < (i+1)*delta:
                            return self.getValue(node.children[i], a)
    
    def testID3(self, tree, data):
        correct = 0
        totalTreePos = 0
        treeTruePos = 0
        for a in data:
            actualValue = a.label
            treeValue = 0
            if tree.root.feature[0:2] == "b_":
                if a[tree.root.feature] == 0:
                    treeValue = self.getValue(tree.root.left, a)
                else:
                    treeValue = self.getValue(tree.root.right, a)
            elif tree.root.feature[0:2] == "y_":
                y = self.yearStart
                delta = self.yearBinSize
                i = 0
                while y <= 2011:
                    if a[tree.root.feature] >= y and a[tree.root.feature] < y+delta:
                        treeValue = self.getValue(tree.root.children[i], a)
                        break
                    y += delta
                    i += 1
            else:
                delta = float(1)/(float(self.realBins))
                for i in range(0, self.realBins):
                    if tree.root.feature in a.keys():
                        if a[tree.root.feature] >= (i)*delta and a[tree.root.feature] < (i+1)*delta:
                            treeValue = self.getValue(tree.root.children[i], a)
                            break
            if(treeValue == actualValue):
                correct+= 1
            if treeValue == 1:
                totalTreePos += 1
                if actualValue == 1:
                    treeTruePos += 1
        return correct, treeTruePos, totalTreePos
    
    def maxChildDepths(self, depths):
        maxD = float(-9999999)
        for d in depths:
            if d > maxD:
                maxD = d
        return maxD
    
    def maxDepth(self, node):
        if(not(node.value == 0)):
            return 1
        elif node.feature[0:2] == "b_":
            lDepth = self.maxDepth(node.left)
            rDepth = self.maxDepth(node.right)
            if(lDepth > rDepth):
                return lDepth + 1
            else:
                return rDepth + 1
        else:
            depths = []
            for c in node.children:
                depths.append(self.maxDepth(c))
            maxD = self.maxChildDepths(depths)
            return maxD + 1
    
    def postPrune(self, node, d):
        if(self.maxDepth(node) <= d):
            return node
        if(d == 1):
            #edit node to be leaf and return
            value = -1 if (node.nots >= node.hots) else 1
            node.value = value
            return node
        if node.feature[0:2] == "b_":
            node.left = self.postPrune(node.left, d-1)
            node.right = self.postPrune(node.right, d-1)
        else:
            for c in node.children:
                c = self.postPrune(c, d-1)
        return node
    
    def train(self, trainData):
        print "Training tree..."
        root = self.runID3(trainData)
        self.root = root
        print "ROOT FEATURE " + str(root.feature)
        print "Done training."
    
    def printTree(self, node, level):
        i = 0
        ind = ""
        while i <= level:
            ind += "-"
            i += 1
        print ind + "node feature: (" + str(node.feature) + ") data: [" + str(node.hots) + "+, " + str(node.nots) + "-]"
        if node.feature[0:2] == "b_":
            if not(node.left.value == 0):
                print ind + "LEFT LEAF " + str(node.left.value)
            else:
                self.printTree(node.left, level+1)
            if not(node.right.value == 0):
                print ind + "RIGHT LEAF " + str(node.right.value)
            else:
                self.printTree(node.right, level+1)
        else:
            for c in node.children:
                if not(c.value == 0):
                    print ind + "LEAF " + str(c.value)
                else:
                    self.printTree(c, level+1)
    
    def printRootTree(self):
        print "Tree:"
        print "root node feature: (" + str(self.root.feature)  + ") data: [" + str(self.root.hots) + "+, " + str(self.root.nots) + "-]"
        if self.root.feature[0:2] == "b_":
            if not(self.root.left.value == 0):
                print "-LEFT LEAF " + str(self.root.left.value)
            else:
                self.printTree(self.root.left, 1)
                #print "root node's left child node feature: (" + str(self.root.left.feature) + ") data: [" + str(self.root.left.hots) + "+, " + str(self.root.left.nots) + "-]"
            if not(self.root.right.value == 0):
                print "-RIGHT LEAF " + str(self.root.right.value)
            else:
                self.printTree(self.root.right, 1)
                #print "root node's right child node feature: (" + str(self.root.right.feature) + ") data: [" + str(self.root.right.hots) + "+, " + str(self.root.right.nots) + "-]"
        else:
            for c in self.root.children:
                if not(c.value == 0):
                    print "-LEAF " + str(c.value)
                else:
                    self.printTree(c, 1)
                    #print "root node's child node feature: (" + str(c.feature) + ") data: [" + str(c.hots) + "+, " + str(c.nots) + "-]"
        print "total # nodes (including leaves): " + str(self.nodes)
        print "total # leaves: " + str(self.leaves)
        maxDep = self.maxDepth(self.root)
        print "max depth: " + str(maxDep)
    
    def printTreeSum(self):
        print "Tree:"
        print "root node feature: (" + str(self.root.feature)  + ") data: [" + str(self.root.hots) + "+, " + str(self.root.nots) + "-]"
        if self.root.feature[0:2] == "b_":
            if not(self.root.left.value == 0):
                print "-LEFT LEAF " + str(self.root.left.value)
            else:
                print "root node's left child node feature: (" + str(self.root.left.feature) + ") data: [" + str(self.root.left.hots) + "+, " + str(self.root.left.nots) + "-]"
                if self.root.left.feature[0:2] == "b_":
                    if not(self.root.left.left.value == 0):
                        print "--LEFT LEAF " + str(self.root.left.left.value)
                    else:
                        print "left child's left child node feature: (" + str(self.root.left.left.feature) + ") data: [" + str(self.root.left.left.hots) + "+, " + str(self.root.left.left.nots) + "-]"
                    if not(self.root.left.right.value == 0):
                        print "--RIGHT LEAF " + str(self.root.left.right.value)
                    else:
                        print "left child's right child node feature: (" + str(self.root.left.right.feature) + ") data: [" + str(self.root.left.right.hots) + "+, " + str(self.root.left.right.nots) + "-]"
                else:
                    for c in self.root.left.children:
                        if not(c.value == 0):
                            print "--LEAF " + str(c.value)
                        else:
                            print "left child's child node feature: (" + str(c.feature) + ") data: [" + str(c.hots) + "+, " + str(c.nots) + "-]"
            if not(self.root.right.value == 0):
                print "-RIGHT LEAF " + str(self.root.right.value)
            else:
                print "root node's right child node feature: (" + str(self.root.right.feature) + ") data: [" + str(self.root.right.hots) + "+, " + str(self.root.right.nots) + "-]"
                if self.root.right.feature[0:2] == "b_":
                    if not(self.root.right.left.value == 0):
                        print "--LEFT LEAF " + str(self.root.right.left.value)
                    else:
                        print "right child's left child node feature: (" + str(self.root.right.left.feature) + ") data: [" + str(self.root.right.left.hots) + "+, " + str(self.root.right.left.nots) + "-]"
                    if not(self.root.right.right.value == 0):
                        print "--LEFT LEAF " + str(self.root.right.right.value)
                    else:
                        print "right child's left child node feature: (" + str(self.root.right.right.feature) + ") data: [" + str(self.root.right.right.hots) + "+, " + str(self.root.right.right.nots) + "-]"
                else:
                    for c in self.root.right.children:
                        if not(c.value == 0):
                            print "--LEAF " + str(c.value)
                        else:
                            print "right child's child node feature: (" + str(c.feature) + ") data: [" + str(c.hots) + "+, " + str(c.nots) + "-]"
        else:
            for c in self.root.children:
                if not(c.value == 0):
                    print "-LEAF " + str(c.value)
                else:
                    print "root node's child node feature: (" + str(c.feature) + ") data: [" + str(c.hots) + "+, " + str(c.nots) + "-]"
        maxDep = self.maxDepth(self.root)
        print "max depth: " + str(maxDep)
    
    def test(self, tree, testData):
        #print "Testing..."
        #print "Tree max depth: " + str(self.maxDepth(tree.root))
        testCorrect, treeTruePos, totalTreePos = self.testID3(tree, testData)
        if totalTreePos < 1:
            totalTreePos = 1
        accuracy = float(testCorrect)/float(len(testData))
        precision = float(treeTruePos)/float(totalTreePos)
        print "correct: " + str(int(testCorrect)) + " total: " + str(len(testData)) + " accuracy = " + str(accuracy)
        print "tree correctly predicted hot: " + str(treeTruePos) + " num tree hot: " + str(totalTreePos) + " precision = " + str(precision)
        return (accuracy, precision)
    
class Node(ID3):
    def __init__(self, v=0, left=None, right=None, feature="", n=0, h=0, children=[]):
        self.feature = feature
        self.hots = h
        self.nots = n
        self.value = v
        self.left = left
        self.right = right
        self.children = children

def getData():
    print "Loading data..."
    f = open('train.pkl')
    trainData = pickle.load(f)
    f.close()
    f = open('test.pkl')
    testData = pickle.load(f)
    f.close()
    print "success"
    return trainData, testData

def trainDT(data):
    node = Node()
    tree = ID3(node)
    tree.train(data)
    return tree

def main():
    trainData, testData = getData()
    tree = trainDT(trainData)
    tree.test(tree, testData)
    #tree.printTreeSum()
    #print "pruning to depth 5"
    #tree.postPrune(tree.root, 5)
    #tree.test(tree, testData)
    tree.printRootTree()

main()