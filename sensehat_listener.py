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

def handle_post_body(body):
    global t
    data = json.loads(body)
    q.put(data)

def worker():
    while True:
        data = q.get()
        if "map" in data:
            processGrid(data)
        elif "string" in data:
            if(len(data["string"])>32):
                data["string"] = data["string"][:32]
            processString(data)
        elif "sequence" in data:
            if(len(data["sequence"])>256):
                data["sequence"] = data["sequence"][:256]
            processSeq(data)
        elif "default" in data:
            processDefault(data)
        elif "flash" in data:
            processFlash(data)
        elif "scroll" in data:
            processScroll(data)
        elif "spin" in data:
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
        else:
            if "colour" not in step:
                step["colour"] = (0,0,0)
            if "x" not in step: step["x"] = 0
            if "y" not in step: step["y"] = 0
            sense.set_pixel(step["x"], step["y"], step["colour"])
        delay = min(1, step["delay"]) if "delay" in step else DEFAULT_SEQ_DELAY
        time.sleep(delay)
    time.sleep(SEQ_FINAL_PAUSE) # Hold final state
    sense.clear()
    time.sleep(DELAY_BETWEEN_HANDLERS)

def processDefault(data):
    # Take a Pixel, set of Pixels or Map and copy into the default screen state
    # Default screen state shows when no other events are being handled
    # Default screen will last until changed
    if "pixels" in data["default"]:
        for pixel in data["default"]["pixels"]:
            if "colour" not in pixel:
                pixel["colour"] = (0,0,0)
            if "x" not in pixel: pixel["x"] = 0
            if "y" not in pixel: pixel["y"] = 0
            defaultScreen[pixel["y"]*8+pixel["x"]] = pixel["colour"]
    elif "map" in data["default"]:
        defaultScreen = formatMap(data["default"]["map"])
    else:
        if "colour" not in data["default"]:
            data["default"]["colour"] = (0,0,0)
        if "x" not in data["default"]: data["default"]["x"] = 0
        if "y" not in data["default"]: data["default"]["y"] = 0
        defaultScreen[data["default"]["y"]*8+data["default"]["x"]] = data["default"]["colour"]

def processFlash(data):
    # Take a Map and flash according to given delays
    inmap = data["flash"]
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
    inmap = make2d(formatMap(data["scroll"]))
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
    inmap = make2d(formatMap(data["spin"]))
    delay = data["delay"] if "delay" in data else DEFAULT_ROTATE_DELAY
    loops = data["loops"] if "loops" in data else DEFAULT_ROTATE_LOOPS
    steps = [
        {"map":inmap,"delay":delay},
        {"map":rotateMap(inmap,90),"delay":delay},
        {"map":rotateMap(inmap,180),"delay":delay},
        {"map":rotateMap(inmap,270),"delay":delay},
    ]
    if "counterclockwise" in data and data["counterclockwise"].lower()=="true":
        steps = [steps[0]]+steps[1:][::-1]
    sequence = steps*loops
    processSeq({"sequence":sequence})

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


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n",str(self.path), str(self.headers))
        logging.debug("POST Body:\n%s\n", post_data.decode('utf-8'))
        handle_post_body(post_data.decode('utf-8'))

        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

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
