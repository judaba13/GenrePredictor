class DataPoint(dict):
	def __init__(self, other):
		dict.__init__(self, other)
		self.familiarity = self['artist_familiarity']
		self.hotttnesss = self['artist_hotttnesss']
		self.artist_id = self['artist_id']
		self.artist_location = self['artist_location']
		self.track_ids = self['track_id']
		self.artist_name = self['artist_name']
		del self['track_id']
		del self['artist_name']
		del self['artist_id']
		del self['artist_location']
		del self['artist_familiarity']
		del self['artist_hotttnesss']

"""
for d in data: # datapoint d, data as a list of Datapoint
 	for feature in d: # feature is feature name as string / key in dict
 		# do stuff with the feature/value pair
 		# d[feature] is value as float 

"""