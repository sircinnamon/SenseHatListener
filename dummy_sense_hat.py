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