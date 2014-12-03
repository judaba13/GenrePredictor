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

def normalize01(data):
	for f in data[0]:
		vals = map(data, lambda dp: dp[f])
		mi = min(vals)
		mx = max(vals)
		rg = mx - mi
		for dp in data:
			dp[f] = (dp[f]- mi ) / rg

def normalizeZ(data):
	for f in data[0]:
		vals = array(map(data, lambda dp: dp[f]))
		sd = std(vals)
		mn = mean(vals)
		for dp in data:
			dp[f] = (dp[f]-mn)/sd