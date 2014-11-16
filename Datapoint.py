class Datapoint(dict):
	def __init__(self, other):
		dict.__init__(self, other)
		self.familiarity = self['familiarity']
		self.hotttnesss = self['hotttnesss']
		del self['familiarity']
		del self['hotttnesss']