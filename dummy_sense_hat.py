import datetime

class DummySenseHat(object):
	pixels = [[0,0,0]]*64

	def clear(self):
		print("[{}] clear screen".format(datetime.datetime.now().strftime("%H:%M:%S")))
		self.pixels = [[0,0,0]]*64

	def set_rotation(self, deg):
		print("[{}] set rotation {}".format(datetime.datetime.now().strftime("%H:%M:%S"), deg))

	def show_message(self, msg):
		print("[{}] print message \"{}\"".format(datetime.datetime.now().strftime("%H:%M:%S"), msg))

	def set_pixels(self, pix):
		print("[{}] set pixels \"{}\"".format(datetime.datetime.now().strftime("%H:%M:%S"), pix))
		self.pixels = pix

	def get_pixels(self):
		print("[{}] get pixels".format(datetime.datetime.now().strftime("%H:%M:%S")))
		return self.pixels