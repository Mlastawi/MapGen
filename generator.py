import wx
import random
import array
from map import *

#init const
MAP_BASE = 10
SCALE_DOWN = 1
#map size in pixels: 2^MAP_BASE / SCALE DOWN
MAP_SIZE = int((2**MAP_BASE) / SCALE_DOWN)

#levels of chaning 'biome' color
WATER_TRESHOLD = 0.4
COAST_TRESHOLD = WATER_TRESHOLD + 0.01 #WATER_TRESHOLD*0.03
MOUNTAIN_TRESHOLD = 0.8


def diamond_square(baseSize, randDecrease = 0.75, bigDevChance = 0.0005, bifDevFctr = 6, tl = None, tr = None, bl = None, br = None):
	_randomScale = 2**0 #currently useless, will be used to 'glue' maps together
	_randomDecrease = randDecrease #how fast the random factor drops, lower values gives smoother maps
	_bigDevChance = bigDevChance #how often random deviation will be bigger
	_bigDevFactor = bifDevFctr #how much random deviation will be bigger
	
	
	#map initialization
	_mapSize = 2**baseSize + 1
	_map = [ [0.0] * _mapSize for _ in range(_mapSize) ]
	
	#initializing corners
	#top left
	if tl is None:
		_map[0][0] = (random.random() - 0.5)*_randomScale
	else:
		_map[0][0] = tl
	#top right
	if tr is None:
		_map[0][-1] = (random.random() - 0.5)*_randomScale
	else:
		_map[0][-1] = tr
	#bottom left
	if bl is None:
		_map[-1][0] = (random.random() - 0.5)*_randomScale
	else:
		_map[-1][0] = bl
	#bottom right
	if br is None:
		_map[-1][-1] = (random.random() - 0.5)*_randomScale
	else:
		_map[-1][-1] = br
	
	

	#diamond function
	def diamond(size, iter, map, scale):
		i = int(2**(iter-1)) #amount of points to compute
		
		s = int((size-1)/i) #step between computed points
		hs = int(s/2) #half of step
		#i x i points
		for x in range(i):
			for y in range(i):
				posx = hs+s*x
				posy = hs+s*y
				# no need to check boundaries cause diamond middle points are always in array range
				map[posy][posx] = ( map[posy-hs][posx-hs] + map[posy-hs][posx+hs] + map[posy+hs][posx-hs] + map[posy+hs][posx+hs] ) / 4
				if random.random() <= _bigDevChance:
					map[posy][posx] += (random.random() - 0.5) * scale * _bigDevFactor
				else:
					map[posy][posx] += (random.random() - 0.5) * scale
		
		return map	
	
	#square function
	def square(size, iter, map, scale):
		i = int(iter)  #iteration counter
		_c  = 2**i + 1 #columns to compute
		_oC = 2**(i-1) #odd columns to compute
		_eC = _c - _oC #even columns to compute
		
		s = int((size-1)/_oC) #step between computed points
		hs = int(s/2) #half of step
		#there is _c columns
		for x in range(_c): 
			#in even columns: 2^(i-1) points -> odd rows
			if x%2 == 0:
				for y in range(_oC): #using the fact block is square so there is same amount of odd rows as columns
					posx = hs*x
					posy = hs+s*y
					
					#check if current point is on the edge of the map
					if x == 0:
						map[posy][posx] = ( map[posy - hs][posx] + map[posy][posx + hs] + map[posy + hs][posx] ) / 3
					elif x == _c-1:
						map[posy][posx] = ( map[posy - hs][posx] + map[posy][posx - hs] + map[posy + hs][posx] ) / 3
					else:
						map[posy][posx] = ( map[posy - hs][posx] + map[posy][posx - hs] + map[posy][posx + hs] + map[posy + hs][posx]) / 4
			#in odd columns: 2^i+1 points
			else:
				for y in range(_eC): #using the fact block is square so there is same amount of even rows as columns
					posx = hs*x
					posy = s*y
					
					#check if current point is on the edge of the map
					if y == 0:
						map[posy][posx] = ( map[posy][posx - hs] + map[posy][posx + hs] + map[posy + hs][posx] ) / 3
					elif y == 2**(i-1):
						map[posy][posx] = ( map[posy - hs][posx] + map[posy][posx - hs] + map[posy][posx + hs] ) / 3
					else:
						map[posy][posx] = ( map[posy - hs][posx] + map[posy][posx - hs] + map[posy][posx + hs] + map[posy + hs][posx]) / 4
			#add noise
			if random.random() <= _bigDevChance:
				map[posy][posx] += (random.random() - 0.5) * scale * _bigDevFactor
			else:
				map[posy][posx] += (random.random() - 0.5) * scale
		return map
	
	_iter = 0
	for i in range(baseSize):
		_iter += 1
		#decrease 'noise' scale
		_randomScale *= _randomDecrease
		#diamond stage
		_map = diamond(_mapSize,_iter,_map,_randomScale)
		#square stage
		_map = square(_mapSize,_iter,_map,_randomScale)	
	#pprint(map)
	return _map

	
def normalize2d(list):
	resMax = [0] * len(list)
	resMin = [0] * len(list)
	for i in range(len(list)):
		resMax[i] = max(list[i])
		resMin[i] = min(list[i])
		
	_min = min(resMin)
	_max = max(resMax) - _min

	res = [[ (elem - _min) / _max for elem in subl] for subl in list]
	
	return res

def scale_down(map, magnitude):
	if magnitude == 1:
		return map
	
	_size = len(map)
	_newSize = int((_size-1)/magnitude)+1
	res = [ [0] for _ in range(_newSize) ]
	
	for i in range(0,_size,magnitude):
		res[int(i/magnitude)] = map[i][::magnitude]
	
	return res
	
class MapPanel(wx.Panel):	
	def __init__(self, *args, **kwargs):
		super(MapPanel, self).__init__(*args, **kwargs)
		self.map = [None]
		self.bmpMap = None
		self.initUI()
	
	def initUI(self):
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		#self.SetBakcgroundColor('white')
		
	def OnPaint(self, e):
		dc = wx.PaintDC(self)
		dc.DrawBitmap(self.bmpMap,0,0)

		del dc

def MakeBitmapRGB(width, height, arr):
	# Make a bitmap using an array of RGB bytes
	bpp = 3  # bytes per pixel
	bytes = array.array('B', [0] * width*height*bpp)

	for y in range(height):
		for x in range(width):
			offset = y*width*bpp + x*bpp
			try:
				c = int(arr[y][x]*255/1.7)
				v = arr[y][x]
			except:
				print('INDEX OUT OF RANGE y: {0}, x: {1}'.format(y,x))
				return None
			
			r = c

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
					
			bytes[offset + 0] = r
			try:
				bytes[offset + 1] = g
			except:
				print('g: {0}, ad: {1}, v: {2}'.format(g,ad,v))
			bytes[offset + 2] = b
			
	rgbBmp = wx.Bitmap.FromBuffer(width, height, bytes)	
	return rgbBmp

def MakeBitmapRGB2(size, arr):
	bpp = 3  # bytes per pixel
	bytes = array.array('B', [0] * size*size*bpp)

	for y in range(size):
		for x in range(size):
			offset = y*size*bpp + x*bpp
			try:
				r = arr[y][x][0]
				g = arr[y][x][1]
				b = arr[y][x][2]
			except:
				print('INDEX OUT OF RANGE y: {0}, x: {1}'.format(y,x))
				return None
			
			bytes[offset + 0] = r
			bytes[offset + 1] = g
			bytes[offset + 2] = b
			
	rgbBmp = wx.Bitmap.FromBuffer(size, size, bytes)	
	return rgbBmp
	
def glue_arrays(arr1, arr2):
	_totalHeight = len(arr1)# + len(arr2)
	_totalWidth = len(arr1[0]) + len(arr2[0])
	res = [ [0.0] * _totalWidth for _ in range(_totalHeight) ]
	
	for i in range(_totalHeight):
		res[i] = arr1[i]+arr2[i]
	
	return res

app = wx.App()
frame = wx.Frame(None, -1, size = wx.Size(MAP_SIZE,MAP_SIZE))
print('------------')
print('Creating map')
_map1 = diamond_square(MAP_BASE)
_map2 = diamond_square(MAP_BASE, randDecrease = 0.3, bigDevChance = -1)
_hMap = scale_down(_map1, SCALE_DOWN)
_tMap = scale_down(_map2, SCALE_DOWN)
print('Map created')
_hMap = normalize2d(_hMap)
_tMap = normalize2d(_tMap)
print('Map normalized')
mmap = Map(MAP_SIZE, heightMap=_hMap, temperatureMap = _tMap)
mmap.makeColorMap()
print('Creating bitmap')
_bmpMap = MakeBitmapRGB(MAP_SIZE,MAP_SIZE,_hMap)
print('Bitmap created')

mPanel = MapPanel(frame, -1)
mPanel.map = mmap.heightMap
mPanel.bmpMap = _bmpMap

frame.Show()
frame.Centre()
app.MainLoop()