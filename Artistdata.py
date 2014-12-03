HOT_THRESH = 0.425
FAM_THRESH = 0.6

class DataPoint(dict):
	def __init__(self, other):
		dict.__init__(self, other)
		self.familiarity = self['artist_familiarity']
		self.hotttnesss = self['artist_hotttnesss']
		self.artist_id = self['artist_id']
		self.artist_location = self['artist_location']
		self.track_ids = self['track_id']
		self.artist_name = self['artist_name']
		self.years = self['years']
		self.label = 1 if self.hotttnesss >= HOT_THRESH and self.familiarity <= FAM_THRESH else -1
		del self['years']
		del self['track_id']
		del self['artist_name']
		del self['artist_id']
		del self['artist_location']
		del self['artist_familiarity']
		del self['artist_hotttnesss']

	def __sub__(self, other):
		return Datapoint({x: self[x]-other[x] for x in self if other[x]!=None})

"""
for d in data: # datapoint d, data as a list of Datapoint
 	for feature in d: # feature is feature name as string / key in dict
 		# do stuff with the feature/value pair
 		# d[feature] is value as float 

"""