import random
import sys
from Artistdata import *
from numpy import *
from util import *
from matplotlib import pyplot as plt

def cosineSimilarity(x, y):
	return dot(x,y) / (norm(x) * norm(y))

def euclideanSimilarity(x, y):
	return - distance(x,y)	

def kNearest(x, T, k, K):
	ordered = sorted(T, key = lambda y: K(x, y))
	return ordered[-k:]

"""
 x: example to classify
 T: training data 
 k: number of nearest neighbors to consider
 K: two-parameter similarity measure (greater values are more similar)
 returns the label with the most of the k nearest neighbors, ties borken randomly
"""
def classifyMajority(x, T, k, K):
	# votes: a list of labels to tally
	# returns the label with the most votes, ties broken randomly
	def countVotes(votes):
		tallies = {}
		for v in votes:
			if v.label in tallies:
				tallies[v.label] += 1
			else:
				tallies[v.label] = 1
		counts = [(k,v) for k,v in tallies.iteritems()]
		random.shuffle(counts)
		return max(counts, key = lambda t: t[1])[0]
	kNear = kNearest(x,T,k,K)
	return countVotes(kNear)

# Averages k nearest familiarity and hotttnesss, and returns if the values are within the thresholds.  
def classifyRegression(x, T, k, K):
	# near: list of k nearest datapoints
	# returns a tuple of average familiarity, hotttnesss of the near dp's
	def avgFamHot(near):
		fam = hot = 0.
		for dp in near:
			fam += dp.familiarity
			hot += dp.hotttnesss
		return (fam/len(near), hot/len(near))
	kNear = kNearest(x,T,k,K)
	(fam, hot) = avgFamHot(kNear)
	return +1 if hot >= HOT_THRESH and fam <= FAM_THRESH else -1

# returns (accuracy, precision, recall) for a test set X, training set T, similarity meaure K 
def test(X, T, k, K, classify):
	tp = tn = fp = fn = 0.
	for x in X:
		if x.label == classify(x, T, k, K):
			if x.label == +1:
				tp += 1
			else:
				tn += 1
		else:
			if x.label == +1:
				fn += 1
			else:
				fp += 1
	accuracy = (tp + tn) / len(X)
	precision = tp / (tp + fp) if (tp + fp > 0) else None
	recall = tp / (tp + fn) if (tp + fn > 0) else None
	return [accuracy, precision, recall]

def testMajority(X, T, k, K):
	return test(X, T, k, K, classifyMajority)

def testRegression(X, T, k, K):
	return test(X, T, k, K, classifyRegression)

def plotCV(results, f, title):
	x = [results[r][3] for r in results if results[r][0] != None]
	y = [results[r][0] for r in results if results[r][0] != None]
	plt.figure()
	plt.title(title+ ": " + str(f) + "-fold CV Accuracy vs k")
	plt.xlabel("k")
	plt.ylabel("average accuracy")
	plt.plot(x, y, ".")
	plt.savefig(title + " accuracy.png")
	x = [results[r][3] for r in results if results[r][1] != None]
	y = [results[r][1] for r in results if results[r][1] != None]
	plt.figure()
	plt.title(title+ ": " + str(f) + "-fold CV Precision vs k")
	plt.xlabel("k")
	plt.ylabel("average precision")
	plt.plot(x, y, ".")
	plt.savefig(title + " precision.png")

def crossValidate(X, T, kVals, K, testF, f, title):
	random.shuffle(X)
	size = float(len(X))/f
	results = {k:[0., 0., 0.] for k in kVals}
	counts = {k:[0, 0, 0] for k in kVals}
	for i in range(f):
		for k in kVals:
			result = testF(X[0:int(i*size)]+X[int((i+1)*size):], X[int(i*size):int((i+1)*size)], k, K)
			for j in range(3):
				if result[j] != None:
					results[k][j] += result[j]
					counts[k][j] += 1
	for k in kVals:
		for j in range(3):
			if counts[k][j] > 0:
				results[k][j] /= f
			else:
				results[k][j] = None
		results[k].append(k)
	k = max(results, key=lambda r: results[r][0])
	bestAccuracy = results[k]
	print "Best Accuracy: ", bestAccuracy
	k = max(results, key=lambda r: results[r][1])
	bestPrecision = results[k]
	print "Best Precision:", bestPrecision
	k = max(results, key=lambda r: results[r][2])
	bestRecall = results[k]
	print "Best Recall:   ", bestRecall
	plotCV(results, f, title)
	return (testF(X, T, bestAccuracy[3], K), testF(X, T, bestPrecision[3], K), testF(X, T, bestRecall[3], K))

def crossValidMajority(X, T, kVals, K, f, title):
	return crossValidate(X, T, kVals, K, testMajority, f, "kNN Majority "+title)

def crossValidRegresion(X, T, kVals, K, f, title):
	return crossValidate(X, T, kVals, K, testRegression, f, "kNN Regression "+title)

def main():
	import pickle
	print "Loading data..."
	f = open('train.pkl')
	X = pickle.load(f)
	f.close()
	f = open('test.pkl')
	T = pickle.load(f)
	f.close()
	normalize01(X, T)
	kVals = [1,2,3,5,7,10,13,17,21,26,31,37,43,50,57]
	print "Testing euclidean regression..."
	print crossValidRegresion(X, T, kVals, euclideanSimilarity, 7, "Euclidean")
	print "Testing euclidean majority..."
	print crossValidMajority(X, T, kVals, euclideanSimilarity, 7, "Euclidean")
	print "Testing cosine majority..."
	print crossValidMajority(X, T, kVals, cosineSimilarity, 7, "Cosine")
	print "Testing cosine regression..."
	print crossValidRegresion(X, T, kVals, cosineSimilarity, 7, "Cosine")

main()

