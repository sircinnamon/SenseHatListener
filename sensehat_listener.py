#!/usr/bin/env python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import logging
from sense_hat import SenseHat
import json
from threading import Timer, Thread
from Queue import Queue
from copy import deepcopy
import time

sense = SenseHat()
sense.set_rotation(270)
t = Timer(5.0, sense.clear)
q = Queue()
defaultScreen = [[0,0,0]]*64

DELAY_BETWEEN_HANDLERS = 1
MAP_PAUSE = 5
SEQ_FINAL_PAUSE =2
DEFAULT_SEQ_DELAY = 0.1
DEFAULT_FLASH_ONTIME = 0.5
DEFAULT_FLASH_OFFTIME = 0.5
DEFAULT_FLASH_LOOPS = 10
DEFAULT_SCROLL_SPEED = 0.2
DEFAULT_SCROLL_DIRECTION=6
DEFAULT_ROTATE_DELAY=0.3
DEFAULT_ROTATE_LOOPS=4

def handle_post_body(body, path):
    try:
        data = json.loads(body)
    except ValueError as e:
        return {"status": 400, "err":"Invalid JSON"}
    ret = {}
    if(path == "/api/string"):
        if(validStringPost(data)):
            data["mode"] = "string"
            ret = {"status": 200}
        else:
            return {"status": 400}
    elif(path == "/api/map"):
        if(validMapPost(data)):
            data["mode"] = "map"
            ret = {"status": 200}
        else:
            return {"status": 400}
    elif(path == "/api/flash"):
        if(validFlashPost(data)):
            data["mode"] = "flash"
            ret = {"status": 200}
        else:
            return {"status": 400}
    elif(path == "/api/spin"):
        if(validSpinPost(data)):
            data["mode"] = "spin"
            ret = {"status": 200}
        else:
            return {"status": 400}
    elif(path == "/api/scroll"):
        if(validScrollPost(data)):
            data["mode"] = "scroll"
            ret = {"status": 200}
        else:
            return {"status": 400}
    elif(path == "/api/sequence"):
        if(validSequencePost(data)):
            data["mode"] = "sequence"
            ret = {"status": 200}
        else:
            return {"status": 400}
    elif(path == "/api/passive"):
        if(validPassivePost(data)):
            data["mode"] = "passive"
            ret = {"status": 200}
        else:
            return {"status": 400}
    else:
        return {"status": 404}
    q.put(data)
    return ret

def handle_get(req):
    if(req.path == "/api/queue"):
        return {"status":200, "body":handle_get_queue()}
    elif(req.path == "/api/grid"):
        return {"status":200, "body":handle_get_grid()}
    else:
        return {"status":400, "body":{"res": "Not Found"}}

def worker():
    while True:
        data = q.get()
        if data["mode"] == "map":
            processGrid(data)
        elif data["mode"] == "string":
            if(len(data["string"])>32):
                data["string"] = data["string"][:32]
            processString(data)
        elif data["mode"] == "sequence":
            if(len(data["sequence"])>256):
                data["sequence"] = data["sequence"][:256]
            processSeq(data)
        elif data["mode"] == "passive":
            processPassive(data)
        elif data["mode"] == "flash":
            processFlash(data)
        elif data["mode"] == "scroll":
            processScroll(data)
        elif data["mode"] == "spin":
            processSpin(data)
        sense.set_pixels(defaultScreen)
        q.task_done()

def processGrid(data):
    # Take a map and output to LEDs
    sense.set_pixels(formatMap(data["map"]))
    time.sleep(MAP_PAUSE)
    sense.clear()
    time.sleep(DELAY_BETWEEN_HANDLERS)

def processString(data):
    # Take a string and print across LEDs
    text_colour=[255,255,255]
    if("colour" in data):
        text_colour=data["colour"]
    back_colour=[0,0,0]
    if("background" in data):
        back_colour=data["background"]
    scroll_speed=0.1
    if("speed" in data):
        scroll_speed=min(data["speed"], 1)
    sense.show_message(data["string"])
    time.sleep(1+len(data["string"])*0.1)

def processSeq(data):
    # Take a start state and sequence of Pixels or Maps, and play using given delays
    if "start" in data and len(data["start"])==64:
        sense.set_pixels(data["start"])
    for step in data["sequence"]:
        if "pixels" in step:
            for pixel in step["pixels"]:
                if "colour" not in pixel:
                    pixel["colour"] = (0,0,0)
                if "x" not in pixel: pixel["x"] = 0
                if "y" not in pixel: pixel["y"] = 0
                sense.set_pixel(pixel["x"], pixel["y"], pixel["colour"])
        elif "map" in step:
            sense.set_pixels(formatMap(step["map"]))
        elif "pixel" in step:
            if "colour" not in step["pixel"]:
                step["pixel"]["colour"] = (0,0,0)
            if "x" not in step["pixel"]: step["pixel"]["x"] = 0
            if "y" not in step["pixel"]: step["pixel"]["y"] = 0
            sense.set_pixel(step["pixel"]["x"], step["pixel"]["y"], step["pixel"]["colour"])
        delay = min(1, step["delay"]) if "delay" in step else DEFAULT_SEQ_DELAY
        time.sleep(delay)
    time.sleep(SEQ_FINAL_PAUSE) # Hold final state
    sense.clear()
    time.sleep(DELAY_BETWEEN_HANDLERS)

def processPassive(data):
    # Take a Pixel, set of Pixels or Map and copy into the default screen state
    # Default screen state shows when no other events are being handled
    # Default screen will last until changed
    global defaultScreen
    if "pixels" in data:
        for pixel in data["pixels"]:
            if "colour" not in pixel:
                pixel["colour"] = (0,0,0)
            if "x" not in pixel: pixel["x"] = 0
            if "y" not in pixel: pixel["y"] = 0
            defaultScreen[pixel["y"]*8+pixel["x"]] = pixel["colour"]
    elif "map" in data:
        defaultScreen = formatMap(data["map"])
    elif "pixel" in data:
        if "colour" not in data["pixel"]:
            data["pixel"]["colour"] = (0,0,0)
        if "x" not in data["pixel"]: data["pixel"]["x"] = 0
        if "y" not in data["pixel"]: data["pixel"]["y"] = 0
        defaultScreen[data["pixel"]["y"]*8+data["pixel"]["x"]] = data["pixel"]["colour"]

def processFlash(data):
    # Take a Map and flash according to given delays
    inmap = data["map"]
    ontime = data["ontime"] if "ontime" in data else DEFAULT_FLASH_ONTIME
    offtime = data["offtime"] if "offtime" in data else DEFAULT_FLASH_OFFTIME
    loops = data["loops"] if "loops" in data else DEFAULT_FLASH_LOOPS
    onstep = {"map":inmap,"delay":ontime};
    offstep = {"map":[],"delay":offtime};
    sequence = [onstep,offstep]*loops
    processSeq({"sequence":sequence})

def processScroll(data):
    # Take a Map and scroll according to given speed and direction
    # Shifts are clockwise from 12, xy
    shifts = [(0,-1),(1,-1),(1,0),(1,1),(0,1),(-1,1),(-1,0),(-1,-1)]
    inmap = make2d(formatMap(data["map"]))
    direction = data["direction"] if "direction" in data else DEFAULT_SCROLL_DIRECTION
    shift = shifts[direction]
    speed = data["speed"] if "speed" in data else DEFAULT_SCROLL_SPEED
    midstep = {"map":inmap,"delay":speed}
    sequence = [midstep];
    for i in range(8):
        beforeStep = shiftMap(sequence[0]["map"],-shift[0],-shift[1])
        afterStep = shiftMap(sequence[-1]["map"],shift[0],shift[1])
        sequence = [{"map":beforeStep,"delay":speed}] + sequence + [{"map":afterStep,"delay":speed}]
    processSeq({"sequence":sequence})

def processSpin(data):
    # Take a Map and rotate 90 degrees on a given time and amount of loops
    inmap = make2d(formatMap(data["map"]))
    delay = data["delay"] if "delay" in data else DEFAULT_ROTATE_DELAY
    loops = data["loops"] if "loops" in data else DEFAULT_ROTATE_LOOPS
    steps = [
        {"map":inmap,"delay":delay},
        {"map":rotateMap(inmap,90),"delay":delay},
        {"map":rotateMap(inmap,180),"delay":delay},
        {"map":rotateMap(inmap,270),"delay":delay},
    ]
    if "counterclockwise" in data and data["counterclockwise"]:
        steps = [steps[0]]+steps[1:][::-1]
    sequence = steps*loops
    processSeq({"sequence":sequence})

def handle_get_queue():
    return {"length": len(q.queue)}

def handle_get_grid():
    return {"map": make2d(sense.get_pixels())}

def formatMap(arr):
    # Parse an array with omitted default values (rows or black values)
    # Detect 2d array vs flat array
    outmap = [[0,0,0]]*64
    two_d = None
    for index, i in enumerate(arr):
        if(len(i)>0):
            if isinstance(i[0],list):
                # This is a 2d arr
                if(two_d == False):return outmap
                two_d = True
                for innerindex, j in enumerate(i):
                    if(len(j)>0):
                        outmap[(8*index + innerindex)] = formatRGB(j)
            else:
                # Can't switch modes
                if(two_d == True):return outmap
                two_d = False
                outmap[index] = formatRGB(i)
    return outmap

def formatRGB(rgb):
    out = [0,0,0]
    if(not isinstance(rgb, list)): return out
    for i in range(min(len(rgb),3)):
        if(not isinstance(rgb[i], int)):
            continue
        out[i] = min(max(rgb[i], 0),255)
    return out

def make2d(arr):
    # Make 64 len array an 8x8
    outarr = []
    for i in range(8):
        outarr.append([])
        for j in range(8):
            outarr[i].append([])
            outarr[i][j] = arr[8*i+j];
    return outarr;

def shiftMap(m, x, y):
    # Shift 8x8 arr by given x and y filling w/ 0s
    newmap = deepcopy(m)
    if abs(y)>0:
        shiftarr(newmap, y, [])
    if abs(x)>0:
        for i in range(len(newmap)):
            newmap[i] = shiftArr(newmap[i], x, [])
    return newmap

def shiftArr(a, i, fill):
    #Shift arr a right by given i
    newlist = list(a)
    amp = abs(i)
    if(amp >= len(a)):return [fill]*len(a)
    if(i>0):
        newlist = [fill]*i + newlist[:-i]
    else:
        newlist = newlist[-(len(a)+i):] + [fill]*amp
    return newlist

def rotateMap(m, deg):
    deg = deg%360;
    if deg%90!=0:
        deg = deg - (deg%90)
    if(deg==0):return m
    newmap = deepcopy(m)
    if(deg==180):
        for i in range(8):
            newmap[i]=newmap[i][::-1]
        newmap = newmap[::-1]
        return newmap
    if(deg==90):
        for i in range(8):
            for j in range(8):
                newmap[i][j] = m[7-j][i]
    if(deg==270):
        for i in range(8):
            for j in range(8):
                newmap[i][j] = m[j][7-i]
    return newmap

def validMap(m):
    # XOR
    return (valid1dMap(m) or valid2dMap(m))

def valid1dMap(m):
    if not isinstance(m, list): return False
    if len(m) > 64: return False
    for item in m:
        if not validRGB(item):
            return False
    return True

def valid2dMap(m):
    if not isinstance(m, list): return False
    if len(m) > 8: return False
    for row in m:
        if not isinstance(row, list): return False
        if len(row) > 8: return False
        for col in row:
            if not validRGB(col):
                return False
    return True

def validRGB(c):
    if not isinstance(c, list): return False
    if len(c) > 3: return False
    for item in c:
        if not isinstance(item, int): return False
        if item < 0:
            return False
        elif item > 255:
            return False
    return True

def validPixel(p):
    if not isinstance(p, dict): return False
    allowed_keys = ["x", "colour", "y"]
    for k in p.keys(): 
        if k not in allowed_keys: return False
    if "colour" in p.keys() and not validRGB(p["colour"]):
        return False
    if "x" in p.keys():
        if not isinstance(p["x"], int): return False
        if p["x"] > 7 or p["x"] < 0: return False
    if "y" in p.keys():
        if not isinstance(p["y"], int): return False
        if p["y"] > 7 or p["y"] < 0: return False
    return True

def validStringPost(p):
    if not isinstance(p, dict): return False
    allowed_keys = ["string", "colour", "background", "speed"]
    if "string" not in p.keys(): return False
    if len(p["string"]) > 32 or len(p["string"]) == 0: return False
    for k in p.keys():
        if k not in allowed_keys: return False
    if "colour" in p.keys() and not validRGB(p["colour"]): return False
    if "background" in p.keys() and not validRGB(p["background"]): return False
    if "speed" in p.keys():
        if p["speed"] > 1 or p["speed"] < 0.01:
            return False
    return True

# Schema Validations

def validMapPost(p):
    if not isinstance(p, dict): return False
    allowed_keys = ["map"]
    for k in p.keys():
        if k not in allowed_keys: return False
    if "map" not in p.keys(): return False
    if not validMap(p["map"]): return False
    return True

def validSequencePost(p):
    if not isinstance(p, dict): return False
    allowed_keys = ["start", "sequence"]
    for k in p.keys():
        if k not in allowed_keys: return False
    if "start" in p.keys() and not validMap(p["start"]): return False
    if "sequence" not in p.keys(): return False
    if not isinstance(p["sequence"], list): return False
    for step in p["sequence"]:
        if not validSequenceStep(step): return False
    return True

def validSequenceStep(p):
    if not isinstance(p, dict): return False
    allowed_keys = ["delay", "map", "pixel", "pixels"]
    for k in p.keys():
        if k not in allowed_keys: return False
    if "delay" in p:
        if not isinstance(p["delay"], float):
            if not isinstance(p["delay"], int): return False
        if (p["delay"] > 1 or p["delay"] < 0): return False
    if "map" in p:
        if "pixel" in p: return False
        if "pixels" in p: return False
        if not validMap(p["map"]): return False
    if "pixel" in p:
        if "map" in p: return False
        if "pixels" in p: return False
        if not validPixel(p["pixel"]): return False
    if "pixels" in p:
        if "map" in p: return False
        if "pixel" in p: return False
        if not isinstance(p["pixels"], list): return False
        if (len(p["pixels"])>64) or (len(p["pixels"])<2): return False
        for px in p["pixels"]:
            if not validPixel(px): return False
    return True

def validPassivePost(p):
    if not isinstance(p, dict): return False
    allowed_keys = ["map", "pixel", "pixels"]
    for k in p.keys():
        if k not in allowed_keys: return False
    if "map" in p:
        if "pixel" in p: return False
        if "pixels" in p: return False
        if not validMap(p["map"]): return False
    if "pixel" in p:
        if "map" in p: return False
        if "pixels" in p: return False
        if not validPixel(p["pixel"]): return False
    if "pixels" in p:
        if "map" in p: return False
        if "pixel" in p: return False
        if not isinstance(p["pixels"], list): return False
        if (len(p["pixels"])>64) or (len(p["pixels"])<2): return False
        for px in p["pixels"]:
            if not validPixel(px["pixel"]): return False
    return True

def validFlashPost(p):
    if not isinstance(p, dict): return False
    allowed_keys = ["map", "ontime", "offtime", "loops"]
    for k in p.keys():
        if k not in allowed_keys: return False
    if "ontime" in p:
        if not isinstance(p["ontime"], float):
            if not isinstance(p["ontime"], int):
                return False
        if (p["ontime"] > 1 or p["ontime"] < 0): return False
    if "offtime" in p:
        if not isinstance(p["offtime"], float):
            if not isinstance(p["offtime"], int):
                return False
        if (p["offtime"] > 1 or p["offtime"] < 0): return False
    if "loops" in p:
        if not isinstance(p["loops"], int): return False
    if "map" not in p: return False
    if not validMap(p["map"]): return False
    return True

def validScrollPost(p):
    if not isinstance(p, dict): return False
    allowed_keys = ["map", "direction", "speed"]
    for k in p.keys():
        if k not in allowed_keys: return False
    if "speed" in p:
        if not isinstance(p["speed"], float):
            if not isinstance(p["speed"], int):
                return False
        if (p["speed"] > 1 or p["speed"] < 0): return False
    if "direction" in p:
        if not isinstance(p["direction"], int): return False
        if p["direction"] < 0 or p["direction"] > 7: return False
    if "map" not in p: return False
    if not validMap(p["map"]): return False
    return True

def validSpinPost(p):
    if not isinstance(p, dict): return False
    allowed_keys = ["map", "counterclockwise", "loops", "delay"]
    for k in p.keys():
        if k not in allowed_keys: return False
    if "counterclockwise" in p:
        if not isinstance(p["counterclockwise"], bool):
            return False
    if "delay" in p:
        if not isinstance(p["delay"], float):
            if not isinstance(p["delay"], int): return False
        if (p["delay"] > 1 or p["delay"] < 0): return False
    if "loops" in p:
        if not isinstance(p["loops"], int): return False
    if "map" not in p: return False
    if not validMap(p["map"]): return False
    return True


class S(BaseHTTPRequestHandler):
    def _set_response(self, code):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, api_key, Authorization')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_response(200)

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        res = handle_get(self)
        self._set_response(res["status"])
        self.wfile.write("{}".format(json.dumps(res["body"])).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n",str(self.path), str(self.headers))
        logging.debug("POST Body:\n%s\n", post_data.decode('utf-8'))
        res = handle_post_body(post_data.decode('utf-8'), self.path)

        self._set_response(res["status"])
        # self.wfile.write('{"res":"POST request for {}"}'.format(self.path).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv
    t = Thread(target=worker)
    t.daemon = True
    t.start()
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
