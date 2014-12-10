import math

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