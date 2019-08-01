import requests
import sensehat_listener
from threading import Thread
import json
import dummy_sense_hat
from time import sleep

dummy = dummy_sense_hat.DummySenseHat()
sensehat_listener.sense = dummy
sensehat_listener.t.cancel()

# Adjust timers so tests can run faster
sensehat_listener.DELAY_BETWEEN_HANDLERS = 0
sensehat_listener.MAP_PAUSE = 0.5
sensehat_listener.SEQ_FINAL_PAUSE =0.5

server = Thread(target=sensehat_listener.run, kwargs={"port":8080})
server.daemon = True
server.start()

worker = Thread(target=sensehat_listener.worker)
worker.daemon = True
worker.start()
sleep(1)

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
		data = {"string": "a", "speed": 0.01}
		r = requests.post(self.base_url, json.dumps(data))
		assert r.status_code == 200
		# Delay so screen and task clear
		sleep(1+len(data["string"])*0.1)

	def test_400(self):
		data = {}
		r = requests.post(self.base_url, json.dumps(data))
		assert r.status_code == 400

class TestMapEndpoint(object):
	base_url = "http://localhost:8080/api/map"

	def test_CORS(self):
		r = requests.options(self.base_url)
		assert "Access-Control-Allow-Origin" in r.headers
		assert "Access-Control-Allow-Methods" in r.headers
		assert "Access-Control-Allow-Headers" in r.headers

	def test_POST(self):
		global dummy
		dummy.set_pixels([[1,1,1]]*64)
		data = {"map": [[255,255,255]]*64}
		r = requests.post(self.base_url, json.dumps(data))
		sleep(0.05)
		r = requests.get("http://localhost:8080/api/grid")
		grid = r.json()["map"]
		assert r.status_code == 200
		assert grid == [[[255,255,255]]*8]*8
		sleep(sensehat_listener.MAP_PAUSE)

	def test_400(self):
		data = {}
		r = requests.post(self.base_url, json.dumps(data))
		assert r.status_code == 400

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

	def test_lengths(self):
		m1 = [[0,0,0]]*64
		m2 = [[[0,0,0]]*8]*8
		assert sensehat_listener.validMap(m1)
		assert sensehat_listener.validMap(m2)
		m1.append([0,0,0])
		m2[0].append([0,0,0])
		assert not sensehat_listener.validMap(m1)
		assert not sensehat_listener.validMap(m2)
		m2 = [[[0,0,0]]*8]*9
		assert not sensehat_listener.validMap(m2)

class TestPixel(object):
	def test_valid(self):
		p = {"x":0, "y":0, "colour":[0,0,0]}
		assert sensehat_listener.validPixel(p)
		p = {"x":7, "y":7, "colour":[]}
		assert sensehat_listener.validPixel(p)

	def test_ranges(self):
		p = {"x":-1, "y":0, "colour":[0,0,0]}
		assert not sensehat_listener.validPixel(p)
		p = {"x":8, "y":7, "colour":[0,0,0]}
		assert not sensehat_listener.validPixel(p)
		p = {"x":0, "y":-1, "colour":[0,0,0]}
		assert not sensehat_listener.validPixel(p)
		p = {"x":7, "y":8, "colour":[0,0,0]}
		assert not sensehat_listener.validPixel(p)

	def test_missing_keys(self):
		p = {"y":0, "colour":[0,0,0]}
		assert not sensehat_listener.validPixel(p)
		p = {"x":7, "colour":[0,0,0]}
		assert not sensehat_listener.validPixel(p)
		p = {"x":0, "y":0}
		assert not sensehat_listener.validPixel(p)
		p = {"x":7}
		assert not sensehat_listener.validPixel(p)
		p = {"y":8}
		assert not sensehat_listener.validPixel(p)
		p = {"colour":[0,0,0]}
		assert not sensehat_listener.validPixel(p)

	def test_extra_keys(self):
		p = {"x":-1, "y":0, "colour":[0,0,0], "key":"val"}
		assert not sensehat_listener.validPixel(p)

class TestStringPostSchema(object):
	def test_minimal_case(self):
		p = {"string":"a"}
		assert sensehat_listener.validStringPost(p)

	def test_all_keys_case(self):
		p = {"string":"a", "colour":[0,0,50], "background":[50,0,0], "speed":0.1}
		assert sensehat_listener.validStringPost(p)

	def test_float_speed_case(self):
		p = {"string":"a", "speed":0.1}
		assert sensehat_listener.validStringPost(p)

	def test_int_speed_case(self):
		p = {"string":"a", "speed":1}
		assert sensehat_listener.validStringPost(p)

	def test_long_string_case(self):
		p = {"string":"abcdefghijklmnopqrstuvwxyz123456"}
		assert sensehat_listener.validStringPost(p)

	# Invalid Cases
	def test_empty_case(self):
		p = {}
		assert not sensehat_listener.validStringPost(p)

	def test_too_long_string_case(self):
		p = {"string":"abcdefghijklmnopqrstuvwxyz1234567"}
		assert not sensehat_listener.validStringPost(p)

	def test_extra_keys(self):
		p = {"string":"abcdefghijklmnopqrstuvwxyz1234567", "badkey":True}
		assert not sensehat_listener.validStringPost(p)

	def test_bad_value_types(self):
		p = {"string":True}
		assert not sensehat_listener.validStringPost(p)
		p = {"string":"Str", "colour":True}
		assert not sensehat_listener.validStringPost(p)
		p = {"string":"Str", "background":True}
		assert not sensehat_listener.validStringPost(p)
		p = {"string":"Str", "speed":"String"} #Bool is a subclass of int apparently
		assert not sensehat_listener.validStringPost(p)

class TestMapPostSchema(object):

	def test_minimal_case(self):
		p = {"map":[[[]]]}
		assert sensehat_listener.validMapPost(p)

	# Invalid Cases
	def test_empty_case(self):
		p = {}
		assert not sensehat_listener.validMapPost(p)

	def test_bad_value_types(self):
		p = {"map":True}
		assert not sensehat_listener.validMapPost(p)
		p = {"map":"Str"}
		assert not sensehat_listener.validMapPost(p)
		p = {"map":{"Dict":"val"}}
		assert not sensehat_listener.validMapPost(p)

	def test_extra_keys(self):
		p = {"map":[[0,0,0]]*64, "badkey":True}
		assert not sensehat_listener.validMapPost(p)

class TestSequencePostSchema(object):

	def test_minimal_case(self):
		p = {"sequence":[{"map":[[[0,0,0]]]}]}
		assert sensehat_listener.validSequencePost(p)

	def test_step_types(self):
		p = {
				"sequence":[
					{"map":[[[0,0,0]]]},
					{"pixel":{"x":0, "y":0, "colour":[0,0,0]}},
					{"pixels":[
						{"x":0, "y":0, "colour":[0,0,0]},
						{"x":1, "y":0, "colour":[0,0,0]},
						{"x":2, "y":0, "colour":[0,0,0]}
					]},
				]
			}
		assert sensehat_listener.validSequencePost(p)

	def test_long_sequence(self):
		p = {
				"sequence":[
					{"map":[[[0,0,0]]]},
					{"pixel":{"x":0, "y":0, "colour":[0,0,0]}},
					{"pixels":[
						{"x":0, "y":0, "colour":[0,0,0]},
						{"x":1, "y":0, "colour":[0,0,0]},
						{"x":2, "y":0, "colour":[0,0,0]}
					]},
				]*20
			}
		assert sensehat_listener.validSequencePost(p)

	def test_start(self):
		p = {
				"start": [[255,255,255]]*64,
				"sequence":[
					{"map":[[[0,0,0]]]}
				]
			}
		assert sensehat_listener.validSequencePost(p)

	def test_bad_value_types(self):
		p = {"sequence":[{"map":[[[0,0,0]]]}], "start":{"pixel":{"x":0, "y":0, "colour":[0,0,0]}}}
		assert not sensehat_listener.validSequencePost(p)
		p = {"sequence":{"map":[[[0,0,0]]]}}
		assert not sensehat_listener.validSequencePost(p)

	def test_extra_keys(self):
		p = {"sequence":[{"map":[[[0,0,0]]]}], "badkey":True}
		assert not sensehat_listener.validSequencePost(p)
		p = {"sequence":[{"map":[[[0,0,0]]]}], "start":[[[0,0,0]]], "badkey":True}
		assert not sensehat_listener.validSequencePost(p)

	def test_missing_required_keys(self):
		p = {"start":[[[0,0,0]]]}
		assert not sensehat_listener.validSequencePost(p)
		p = {}
		assert not sensehat_listener.validSequencePost(p)


class TestSequenceStepSchema(object):
	# Shorthand valid pixels
	p1 = {"x":0, "y":0, "colour":[0,0,0]}
	p2 = {"x":0, "y":1, "colour":[0,0,0]}

	def test_minimal_cases(self):
		p = {"map":[[[0,0,0]]]}
		assert sensehat_listener.validSequenceStep(p)
		p = {"pixel":self.p1}
		assert sensehat_listener.validSequenceStep(p)
		p = {"pixels":[self.p1,self.p2]}
		assert sensehat_listener.validSequenceStep(p)

	def test_delay(self):
		p = {"map":[[[0,0,0]]], "delay": 0}
		assert sensehat_listener.validSequenceStep(p)
		p = {"pixel":self.p1, "delay": 0.5}
		assert sensehat_listener.validSequenceStep(p)
		p = {"pixels":[self.p1,self.p2], "delay": 1}
		assert sensehat_listener.validSequenceStep(p)

	def test_key_conflicts(self):
		p = {"map":[[[0,0,0]]], "pixel":self.p1}
		assert not sensehat_listener.validSequenceStep(p)
		p = {"pixel":self.p1, "pixels":[self.p1,self.p2]}
		assert not sensehat_listener.validSequenceStep(p)
		p = {"pixels":[self.p1,self.p2], "map":[[[0,0,0]]]}
		assert not sensehat_listener.validSequenceStep(p)

	def test_missing_required_keys(self):
		p = {}
		assert not sensehat_listener.validSequenceStep(p)

	def test_delay_range(self):
		p = {"map":[[[0,0,0]]], "delay": -0.01}
		assert not sensehat_listener.validSequenceStep(p)
		p = {"map":[[[0,0,0]]], "delay": 2}
		assert not sensehat_listener.validSequenceStep(p)
		p = {"map":[[[0,0,0]]], "delay": 100}
		assert not sensehat_listener.validSequenceStep(p)

	def test_bad_value_types(self):
		p = {"map":self.p1, "delay": 1}
		assert not sensehat_listener.validSequenceStep(p)
		p = {"pixel":[self.p1,self.p2], "delay": 1}
		assert not sensehat_listener.validSequenceStep(p)
		p = {"pixels":self.p1, "delay": 1}
		assert not sensehat_listener.validSequenceStep(p)
		p = {"pixel":self.p1, "delay": "str"}
		assert not sensehat_listener.validSequenceStep(p)

	def test_extra_keys(self):
		p = {"pixel":self.p1, "delay": 1, "badkey":True}
		assert not sensehat_listener.validSequenceStep(p)
		p = {"pixels":[self.p1,self.p2], "delay": 1, "badkey":True}
		assert not sensehat_listener.validSequenceStep(p)
		p = {"map":[[[0,0,0]]], "badkey":True}
		assert not sensehat_listener.validSequenceStep(p)

class TestPassivePostSchema(object):
	# Shorthand valid pixels
	p1 = {"x":0, "y":0, "colour":[0,0,0]}
	p2 = {"x":0, "y":1, "colour":[0,0,0]}

	def test_minimal_cases(self):
		p = {"map":[[[0,0,0]]]}
		assert sensehat_listener.validPassivePost(p)
		p = {"pixel":self.p1}
		assert sensehat_listener.validPassivePost(p)
		p = {"pixels":[self.p1,self.p2]}
		assert sensehat_listener.validPassivePost(p)

	def test_key_conflicts(self):
		p = {"map":[[[0,0,0]]], "pixel":self.p1}
		assert not sensehat_listener.validPassivePost(p)
		p = {"pixel":self.p1, "pixels":[self.p1,self.p2]}
		assert not sensehat_listener.validPassivePost(p)
		p = {"pixels":[self.p1,self.p2], "map":[[[0,0,0]]]}
		assert not sensehat_listener.validPassivePost(p)

	def test_missing_required_keys(self):
		p = {}
		assert not sensehat_listener.validPassivePost(p)

	def test_bad_value_types(self):
		p = {"map":self.p1}
		assert not sensehat_listener.validPassivePost(p)
		p = {"pixel":[self.p1,self.p2]}
		assert not sensehat_listener.validPassivePost(p)
		p = {"pixels":self.p1}
		assert not sensehat_listener.validPassivePost(p)

	def test_extra_keys(self):
		p = {"pixel":self.p1, "badkey":True}
		assert not sensehat_listener.validPassivePost(p)
		p = {"pixels":[self.p1,self.p2], "badkey":True}
		assert not sensehat_listener.validPassivePost(p)
		p = {"map":[[[0,0,0]]], "badkey":True}
		assert not sensehat_listener.validPassivePost(p)

class TestFlashPostSchema(object):

	def test_minimal_case(self):
		p = {"map":[[[0,0,0]]]}
		assert sensehat_listener.validFlashPost(p)

	def test_all_keys(self):
		p = {"map":[[[0,0,0]]], "ontime":0.1, "offtime":0.1, "loops":2}
		assert sensehat_listener.validFlashPost(p)

	def test_ontime_range(self):
		p = {"map":[[[0,0,0]]], "ontime":0}
		assert sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "ontime":1}
		assert sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "ontime":0.5}
		assert sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "ontime":-0.5}
		assert not sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "ontime":2}
		assert not sensehat_listener.validFlashPost(p)

	def test_offtime_range(self):
		p = {"map":[[[0,0,0]]], "offtime":0}
		assert sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "offtime":1}
		assert sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "offtime":0.5}
		assert sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "offtime":-0.5}
		assert not sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "offtime":2}
		assert not sensehat_listener.validFlashPost(p)

	def test_loops(self):
		p = {"map":[[[0,0,0]]], "loops":0}
		assert sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "loops":1}
		assert sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "loops":20}
		assert sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "loops":0.5}
		assert not sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "loops":-0.5}
		assert not sensehat_listener.validFlashPost(p)

	def test_missing_required_keys(self):
		p = {}
		assert not sensehat_listener.validFlashPost(p)
		p = {"loops":1}
		assert not sensehat_listener.validFlashPost(p)
		p = {"ontime":1}
		assert not sensehat_listener.validFlashPost(p)
		p = {"offtime":1}
		assert not sensehat_listener.validFlashPost(p)
		p = {"ontime":0.1, "offtime":0.1, "loops":2}
		assert not sensehat_listener.validFlashPost(p)

	def test_bad_value_types(self):
		p = {"map":{}, "ontime":0.1, "offtime":0.1, "loops":2}
		assert not sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "ontime":"str", "offtime":0.1, "loops":2}
		assert not sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "ontime":0.1, "offtime":"str", "loops":2}
		assert not sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]], "ontime":0.1, "offtime":0.1, "loops":"str"}
		assert not sensehat_listener.validFlashPost(p)

	def test_extra_keys(self):
		p = {"map":[[[0,0,0]]], "badkey":0.1}
		assert not sensehat_listener.validFlashPost(p)
		p = {"map":[[[0,0,0]]],"ontime":0.1, "offtime":0.1, "loops":2, "badkey":1}
		assert not sensehat_listener.validFlashPost(p)


class TestScrollPostSchema(object):

	def test_minimal_case(self):
		p = {"map":[[[0,0,0]]]}
		assert sensehat_listener.validScrollPost(p)

	def test_all_keys(self):
		p = {"map":[[[0,0,0]]], "direction":1, "speed":1}
		assert sensehat_listener.validScrollPost(p)

	def test_direction(self):
		p = {"map":[[[0,0,0]]], "direction":0}
		assert sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "direction":1}
		assert sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "direction":5}
		assert sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "direction":7}
		assert sensehat_listener.validScrollPost(p)
		# Invalid
		p = {"map":[[[0,0,0]]], "direction":-1}
		assert not sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "direction":8}
		assert not sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "direction":0.5}
		assert not sensehat_listener.validScrollPost(p)

	def test_speed_range(self):
		p = {"map":[[[0,0,0]]], "speed":0}
		assert sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "speed":1}
		assert sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "speed":0.5}
		assert sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "speed":-0.5}
		assert not sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "speed":2}
		assert not sensehat_listener.validScrollPost(p)

	def test_missing_required_keys(self):
		p = {"direction":1, "speed":1}
		assert not sensehat_listener.validScrollPost(p)
		p = {"direction":1}
		assert not sensehat_listener.validScrollPost(p)
		p = {"speed":1}
		assert not sensehat_listener.validScrollPost(p)

	def test_bad_value_types(self):
		p = {"map":{}, "direction":1, "speed":1}
		assert not sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "direction":"str", "speed":1}
		assert not sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "direction":1, "speed":"str"}
		assert not sensehat_listener.validScrollPost(p)

	def test_extra_keys(self):
		p = {"map":[[[0,0,0]]], "badkey":0.1}
		assert not sensehat_listener.validScrollPost(p)
		p = {"map":[[[0,0,0]]], "direction":1, "speed":1, "badkey":True}
		assert not sensehat_listener.validScrollPost(p)


class TestSpinPostSchema(object):

	def test_minimal_case(self):
		p = {"map":[[[0,0,0]]]}
		assert sensehat_listener.validSpinPost(p)

	def test_all_keys(self):
		p = {"map":[[[0,0,0]]], "loops":1, "delay":1, "counterclockwise":True}
		assert sensehat_listener.validSpinPost(p)

	def test_loops(self):
		p = {"map":[[[0,0,0]]], "loops":0}
		assert sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "loops":1}
		assert sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "loops":20}
		assert sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "loops":0.5}
		assert not sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "loops":-0.5}
		assert not sensehat_listener.validSpinPost(p)

	def test_delay_range(self):
		p = {"map":[[[0,0,0]]], "delay":0}
		assert sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "delay":1}
		assert sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "delay":0.5}
		assert sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "delay":-0.5}
		assert not sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "delay":2}
		assert not sensehat_listener.validSpinPost(p)

	def test_counterclockwise(self):
		p = {"map":[[[0,0,0]]], "counterclockwise":True}
		assert sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "counterclockwise":False}
		assert sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "counterclockwise":"str"}
		assert not sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "counterclockwise":{}}
		assert not sensehat_listener.validSpinPost(p)

	def test_missing_required_keys(self):
		p = {"loops":1, "delay":1, "counterclockwise":True}
		assert not sensehat_listener.validSpinPost(p)
		p = {"delay":1, "counterclockwise":True}
		assert not sensehat_listener.validSpinPost(p)
		p = {"loops":1, "counterclockwise":True}
		assert not sensehat_listener.validSpinPost(p)
		p = {"loops":1, "delay":1}
		assert not sensehat_listener.validSpinPost(p)
		p = {"loops":1}
		assert not sensehat_listener.validSpinPost(p)
		p = {"delay":1}
		assert not sensehat_listener.validSpinPost(p)
		p = {"counterclockwise":True}
		assert not sensehat_listener.validSpinPost(p)

	def test_bad_value_types(self):
		p = {"map":{}, "loops":1, "delay":1, "counterclockwise":True}
		assert not sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "loops":"0.1", "delay":1, "counterclockwise":True}
		assert not sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "loops":1, "delay":"str", "counterclockwise":True}
		assert not sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "loops":1, "delay":1, "counterclockwise":"True"}
		assert not sensehat_listener.validSpinPost(p)

	def test_extra_keys(self):
		p = {"map":[[[0,0,0]]], "badkey":0.1}
		assert not sensehat_listener.validSpinPost(p)
		p = {"map":[[[0,0,0]]], "loops":1, "delay":1, "counterclockwise":True, "badkey":True}
		assert not sensehat_listener.validSpinPost(p)