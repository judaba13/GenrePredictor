from util import *
import subprocess
import re
import random
from matplotlib import pyplot as plt

k = 7
C = [0., 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.011, 0.012, 0.013, 0.014, 0.015, 0.016, 0.017, 0.018, 0.019, 0.02, .021, .022, .023, .024, .025]
J = [1., 1.05, 1.1, 1.15, 1.2, 1.25, 1.3, 1.35, 1.4, 1.45, 1.5, 1.65, 1.7, 1.75, 1.8, 1.85, 1.9, 1.95, 2.]

X, T = loadData()

def test(X, T, c, j):
	toSVMLight('test.txt', T)
	toSVMLight("train.txt", X)
	subprocess.check_output("./svm_learn -c {0} -j {1} train.txt".format(c, j), shell=True)
	result = subprocess.check_output("./svm_classify test.txt svm_model svm_out.txt", shell=True)
	match = re.search(r"Accuracy on test set: ([\d\.]+)%\s+", result)
	a = float(match.group(1))/100 if match else None
	match = re.search(r"Precision/recall on test set: ([\d\.]+)%/[\d\.]+%\s+", result)
	p = float(match.group(1))/100 if match else None
	return [a, p]

def plotCV(results, title, bestAccuracy, bestPrecision):
	x = [results[(c, bestAccuracy[2][1])][2][0] for c in C if results[(c, bestAccuracy[2][1])][0] != None]
	y = [results[(c, bestAccuracy[2][1])][0] for c in C if results[(c, bestAccuracy[2][1])][0] != None]
	plt.figure()
	plt.title(title+ ": " + str(k) + "-fold CV Accuracy vs C, j="+str(bestAccuracy[2][1]))
	plt.xlabel("C")
	plt.ylabel("average accuracy")
	plt.plot(x, y, ".")
	plt.savefig(title + " accuracy C.png")
	x = [results[(c, bestPrecision[2][1])][2][0] for c in C if results[(c, bestPrecision[2][1])][1] != None]
	y = [results[(c, bestPrecision[2][1])][1] for c in C if results[(c, bestPrecision[2][1])][1] != None]
	plt.figure()
	plt.title(title+ ": " + str(k) + "-fold CV Precision vs C, j="+str(bestPrecision[2][1]))
	plt.xlabel("C")
	plt.ylabel("average precision")
	plt.plot(x, y, ".")
	plt.savefig(title + " precision C.png")
	x = [results[(bestAccuracy[2][0], j)][2][1] for j in J if results[(bestAccuracy[2][0], j)][0] != None]
	y = [results[(bestAccuracy[2][0], j)][0] for j in J if results[(bestAccuracy[2][0], j)][0] != None]
	plt.figure()
	plt.title(title+ ": " + str(k) + "-fold CV Accuracy vs j, C="+str(bestAccuracy[2][0]))
	plt.xlabel("j")
	plt.ylabel("average accuracy")
	plt.plot(x, y, ".")
	plt.savefig(title + " accuracy j.png")
	x = [results[(bestPrecision[2][0], j)][2][1] for j in J if results[(bestPrecision[2][0], j)][1] != None]
	y = [results[(bestPrecision[2][0], j)][1] for j in J if results[(bestPrecision[2][0], j)][1] != None]
	plt.figure()
	plt.title(title+ ": " + str(k) + "-fold CV Precision vs j, C="+str(bestPrecision[2][0]))
	plt.xlabel("j")
	plt.ylabel("average precision")
	plt.plot(x, y, ".")
	plt.savefig(title + " precision j.png")

#print "normalizing..."
#normalize01(X, [])
random.shuffle(X)
size = float(len(X))/k
results = {(c,j):[0., 0.] for c in C for j in J}
counts = {(c,j):[0, 0] for c in C for j in J}
for i in range(k):
	for c in C:
		for j in J:
			result = test(X[0:int(i*size)]+X[int((i+1)*size):], X[int(i*size):int((i+1)*size)], c, j)
			for l in range(2):
				if result[l] != None:
					results[(c, j)][l] += result[l]
					counts[(c, j)][l] += 1
for c in C:
	for j in J:
		for l in range(2):	
			if counts[(c,j)][l] > 0:
				results[(c,j)][l] /= k
			else:
				results[(c,j)][l] = None
		results[(c,j)].append((c,j))
p = max(results, key=lambda r: results[r][0])
bestAccuracy = results[p]
print "Best Accuracy: ", bestAccuracy
print test(X, T, *bestAccuracy[2])
p = max(results, key=lambda r: results[r][1])
bestPrecision = results[p]
print "Best Precision:", bestPrecision
print test(X, T, *bestPrecision[2])
plotCV(results, "SVM", bestAccuracy, bestPrecision)