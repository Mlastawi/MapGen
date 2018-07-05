class Map:
	heightMap = None
	temperatureMap = None
	biomeMap = None
	colorMap = None
	size = None	
	
	
	
	
	
	def __init__(self, size = 1, **kwargs):#, heightMap = None, temperatureMap = None):
		self.size = size
		self.heightMap = kwargs.get('heightMap')
		self.temperatureMap = kwargs.get('temperatureMap')
	
	def makeColorMap(self):
		if self.heightMap is None or self.temperatureMap is None:
			print('No base maps')
			return None
		
		self.colorMap = [[[0, 0, 0]] * self.size for _ in range(self.size)]
		
		WATER_TRESHOLD = 0.4
		COAST_TRESHOLD = WATER_TRESHOLD + 0.01 #WATER_TRESHOLD*0.03
		MOUNTAIN_TRESHOLD = 0.8
		for y in range(self.size):
			for x in range(self.size):
				try:
					h = int(self.heightMap[y][x]*255/1.7)
					v = self.heightMap[y][x]
				except:
					print('INDEX OUT OF RANGE y: {0}, x: {1}'.format(y,x))
					return None
				
				r = h

				if v <= WATER_TRESHOLD:
						b = 255 - int((WATER_TRESHOLD - v) * 128 / WATER_TRESHOLD)
						border = WATER_TRESHOLD*3/4
						ad = int(( v - border ) * 128/(WATER_TRESHOLD/4))
						g = max(0, ad)
				elif v <= COAST_TRESHOLD:
						g = 223
						r = 223
						b = 128
				elif v <= MOUNTAIN_TRESHOLD:
						
						border = MOUNTAIN_TRESHOLD - COAST_TRESHOLD
						
						ad = int((v - COAST_TRESHOLD)*64/(MOUNTAIN_TRESHOLD - COAST_TRESHOLD))
						#b = max(0, ad)
						b = 0#int((v - COAST_TRESHOLD)*32/(MOUNTAIN_TRESHOLD - COAST_TRESHOLD))
						g = 72 + ad
				else:
						_mV = v - MOUNTAIN_TRESHOLD
						_redBorder = int(255 * MOUNTAIN_TRESHOLD/1.7)
						_greenBorder = 72 + 64
						_blueBorder = 0
						_peakValue = 212
						g = _greenBorder - int(_mV * (_greenBorder-_peakValue)/(1-MOUNTAIN_TRESHOLD))
						r = _redBorder - int(_mV * (_redBorder-_peakValue)/(1-MOUNTAIN_TRESHOLD))
						b = _blueBorder - int(_mV * (_blueBorder-_peakValue)/(1-MOUNTAIN_TRESHOLD))
						
				self.colorMap[y][x][0] = r
				self.colorMap[y][x][1] = g
				self.colorMap[y][x][2] = b
		