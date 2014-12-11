import math
import pickle

def dot(x, y):
	total = 0.
	for f in x:
		if f in y:
			total += x[f] * y[f]
	return total

def norm(x):
	return math.sqrt(dot(x, x))

def distance(x, y):
	return norm(x - y)

def normalize01(data, data1):
	for f in data[0]:
		vals = map(lambda dp: dp[f], data) + map(lambda dp: dp[f], data1)
		mi = min(vals)
		mx = max(vals)
		rg = mx - mi
		if rg > 0:
			for dp in data:
				dp[f] = (dp[f]- mi ) / rg
			for dp in data1:
				dp[f] = (dp[f]- mi ) / rg

def normalizeZ(data):
	for f in data[0]:
		vals = array(map(lambda dp: dp[f], data))
		sd = std(vals)
		mn = mean(vals)
		for dp in data:
			dp[f] = (dp[f]-mn)/sd

def toSVMLight(path, testdata):
	testfile = open(path, 'w')
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
		testfile.write('# \n')
	testfile.close()

def loadData():
	print "Loading data..."
	f = open('train_raw.pkl', 'rb')
	X = pickle.load(f)
	f.close()
	f = open('test_raw.pkl', 'rb')
	T = pickle.load(f)
	f.close()
	return (X, T)