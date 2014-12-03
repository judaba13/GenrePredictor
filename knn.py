import random
from Artistdata import *
from numpy import *
from util import *

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
	return (accuracy, precision, recall)

def testMajority(X, T, k, K):
	return test(X, T, k, K, classifyMajority)

def testRegression(X, T, k, K):
	return test(X, T, k, K, classifyRegression)

def main():
	import datacollector
	X = datacollector.generate_data()
	print testMajority(X, X, 1, euclideanSimilarity)
	print testRegression(X, X, 1, euclideanSimilarity)
	print testMajority(X, X, 5, euclideanSimilarity)
	print testRegression(X, X, 5, euclideanSimilarity)
	print testMajority(X, X, 10, euclideanSimilarity)
	print testRegression(X, X, 10, euclideanSimilarity)

main()

