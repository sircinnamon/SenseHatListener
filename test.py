import requests
import sensehat_listener
from threading import Thread
import json

class TestCORS(object):
	base_url = "http://localhost:8080/api{}"

	def test_map_endpoint(self):
		url = self.base_url.format("/map")
		r = requests.options(url)
		assert "Access-Control-Allow-Origin" in r.headers
		assert "Access-Control-Allow-Methods" in r.headers
		assert "Access-Control-Allow-Headers" in r.headers

	def test_sequence_endpoint(self):
		url = self.base_url.format("/sequence")
		r = requests.options(url)
		assert "Access-Control-Allow-Origin" in r.headers
		assert "Access-Control-Allow-Methods" in r.headers
		assert "Access-Control-Allow-Headers" in r.headers

	def test_passive_endpoint(self):
		url = self.base_url.format("/passive")
		r = requests.options(url)
		assert "Access-Control-Allow-Origin" in r.headers
		assert "Access-Control-Allow-Methods" in r.headers
		assert "Access-Control-Allow-Headers" in r.headers

	def test_scroll_endpoint(self):
		url = self.base_url.format("/scroll")
		r = requests.options(url)
		assert "Access-Control-Allow-Origin" in r.headers
		assert "Access-Control-Allow-Methods" in r.headers
		assert "Access-Control-Allow-Headers" in r.headers

	def test_spin_endpoint(self):
		url = self.base_url.format("/spin")
		r = requests.options(url)
		assert "Access-Control-Allow-Origin" in r.headers
		assert "Access-Control-Allow-Methods" in r.headers
		assert "Access-Control-Allow-Headers" in r.headers

	def test_flash_endpoint(self):
		url = self.base_url.format("/flash")
		r = requests.options(url)
		assert "Access-Control-Allow-Origin" in r.headers
		assert "Access-Control-Allow-Methods" in r.headers
		assert "Access-Control-Allow-Headers" in r.headers

class TestStringEndpoint(object):
	base_url = "http://localhost:8080/api/string"

	def test_CORS(self):
		r = requests.options(self.base_url)
		assert "Access-Control-Allow-Origin" in r.headers
		assert "Access-Control-Allow-Methods" in r.headers
		assert "Access-Control-Allow-Headers" in r.headers

	def test_POST(self):
		data = {"string": "Test", "speed": 0.01}
		r = requests.post(self.base_url, json.dumps(data))
		assert r.status_code == 200

class TestColour(object):

	def test_fully_valid(self):
		colour = [255, 0, 0]
		assert sensehat_listener.formatRGB(colour) == colour
		colour = [255, 255, 0]
		assert sensehat_listener.formatRGB(colour) == colour
		colour = [255, 255, 255]
		assert sensehat_listener.formatRGB(colour) == colour
		colour = [0, 0, 0]
		assert sensehat_listener.formatRGB(colour) == colour
		colour = [1, 2, 3]
		assert sensehat_listener.formatRGB(colour) == colour
		colour = [100, 200, 69]
		assert sensehat_listener.formatRGB(colour) == colour

	def test_padding(self):
		colour = []
		assert sensehat_listener.formatRGB(colour) == [0, 0, 0]
		colour = [0,0,0,0]
		assert sensehat_listener.formatRGB(colour) == [0, 0, 0]
		colour = [255]
		assert sensehat_listener.formatRGB(colour) == [255, 0, 0]
		colour = [255,255]
		assert sensehat_listener.formatRGB(colour) == [255, 255, 0]
		colour = [0,255]
		assert sensehat_listener.formatRGB(colour) == [0, 255, 0]
		colour = [1]
		assert sensehat_listener.formatRGB(colour) == [1, 0, 0]
		colour = [100]
		assert sensehat_listener.formatRGB(colour) == [100, 0, 0]
		colour = [4,3,2,1]
		assert sensehat_listener.formatRGB(colour) == [4, 3, 2]

	def test_range(self):
		colour = [-1,-1,-1]
		assert sensehat_listener.formatRGB(colour) == [0, 0, 0]
		colour = [256,256,256]
		assert sensehat_listener.formatRGB(colour) == [255, 255, 255]
		colour = [-2836759872365789364587]
		assert sensehat_listener.formatRGB(colour) == [0, 0, 0]
		colour = [2836759872365789364587]
		assert sensehat_listener.formatRGB(colour) == [255, 0, 0]


	def test_invalid(self):
		colour = "string"
		assert sensehat_listener.formatRGB(colour) == [0, 0, 0]
		colour = ["arr","of","str"]
		assert sensehat_listener.formatRGB(colour) == [0, 0, 0]
		colour = {"this": "is", "a": "dict"}
		assert sensehat_listener.formatRGB(colour) == [0, 0, 0]
		colour = ["1","2","3"]
		assert sensehat_listener.formatRGB(colour) == [0, 0, 0]

class TestMap(object):
	base_map = [[0,0,0]]*64

	def test_fully_valid(self):
		m1 = [[0,0,0]]*64
		assert sensehat_listener.formatMap(m1) == self.base_map
		m2 = [[[0,0,0]]*8]*8
		m2 = [[[0,0,0]] * 8 for i in range(8)]
		assert sensehat_listener.formatMap(m2) == self.base_map
		m1 = [[255,0,0]]*64
		assert sensehat_listener.formatMap(m1) == m1
		m2 = [[[255,0,0]] * 8 for i in range(8)]
		assert sensehat_listener.formatMap(m2) == [[255,0,0]]*64
		m1[24] = [0,0,255]
		m2[3][0] = [0,0,255]
		assert sensehat_listener.formatMap(m1) == m1
		assert sensehat_listener.formatMap(m2) == m1

	def test_padding(self):
		m1 = []
		m2 = []
		assert sensehat_listener.formatMap(m1) == self.base_map
		assert sensehat_listener.formatMap(m2) == self.base_map
		m1 = [[1,0,0]]
		m2 = [[[1,0,0]]]
		m = [[0,0,0]]*64
		m[0] = [1,0,0]
		assert sensehat_listener.formatMap(m1) == m
		assert sensehat_listener.formatMap(m2) == m
		m1 = [[0,0,0]]*34
		m2 = [[],[],[],[],[]]
		m1[33] = [1,0,0]
		m2[4] = [[],[1,0,0]]
		m = [[0,0,0]]*64
		m[33] = [1,0,0]
		assert sensehat_listener.formatMap(m1) == m
		assert sensehat_listener.formatMap(m2) == m
