import datetime, json
from time import sleep

class DummySenseHat(object):
	pixels = [[0,0,0]]*64

	def clear(self):
		self.pixels = [[0,0,0]]*64
		print("[{}] clear screen".format(datetime.datetime.now().strftime("%H:%M:%S")))

	def set_rotation(self, deg):
		print("[{}] set rotation {}".format(datetime.datetime.now().strftime("%H:%M:%S"), deg))

	def show_message(self,
					 msg,
					 text_colour=[255,255,255],
					 back_colour=[0,0,0],
					 scroll_speed=0.1):
		print("[{}] print message \"{}\"".format(datetime.datetime.now().strftime("%H:%M:%S"), msg))

	def set_pixels(self, pix):
		self.pixels = pix
		print("[{}] set pixels \"{}\"".format(datetime.datetime.now().strftime("%H:%M:%S"), json.dumps(pix)))

	def get_pixels(self):
		print("[{}] get pixels".format(datetime.datetime.now().strftime("%H:%M:%S")))
		return self.pixels

	def set_pixel(self, x, y, *args):
		if len(args) == 1: pixel = list(args[0])
		elif len(args) == 3: pixel = [args[0], args[1], args[2]]
		else: raise ValueError("Invalid rgb argument")
		if x > 7 or x < 0:
		    raise ValueError('X position must be between 0 and 7')
		if y > 7 or y < 0:
		    raise ValueError('Y position must be between 0 and 7')

		print("[{}] set pixel ({},{}) = {}".format(datetime.datetime.now().strftime("%H:%M:%S"), x, y, pixel))
		self.pixels[(8*y)+x] = pixel

	def get_pixel(self, x, y):
		if x > 7 or x < 0:
		    raise ValueError('X position must be between 0 and 7')
		if y > 7 or y < 0:
		    raise ValueError('Y position must be between 0 and 7')
		print("[{}] get pixel ({},{})".format(datetime.datetime.now().strftime("%H:%M:%S"), x, y))
		return self.pixels[(8*y)+x]