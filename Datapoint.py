class Datapoint(dict):
	def __init__(self, other):
		dict.__init__(self, other)
		self.familiarity = self['familiarity']
		self.hotttnesss = self['hotttnesss']
		del self['familiarity']
		del self['hotttnesss']

'''
for d in data: # datapoint d, data as a list of Datapoint
 	for feature in d: # feature is feature name as string / key in dict
 		# do stuff with the feature/value pair
 		# d[feature] is value as float 

'''