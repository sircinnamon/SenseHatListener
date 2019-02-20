#!/usr/bin/env python
"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import logging
from sense_hat import SenseHat
import json
from threading import Timer, Thread
from Queue import Queue
import time

sense = SenseHat()
sense.set_rotation(270)
t = Timer(5.0, sense.clear)
q = Queue();

def handle_post_body(body):
    global t
    data = json.loads(body)
    q.put(data)

def worker():
    while True:
        data = q.get()
        if "map" in data:
            if(len(data["map"])!=64):
                return
            processGrid(data)
        elif "string" in data:
            if(len(data["string"])>32):
                data["string"] = data["string"][:32]
            processString(data);
        elif "sequence" in data:
            if(len(data["sequence"])>256):
                data["sequence"] = data["sequence"][:256]
            processSeq(data);
        q.task_done()

def processGrid(data):
    sense.set_pixels(formatMap(data["map"]));
    # Reset clear timer
    time.sleep(5)
    sense.clear()
    time.sleep(1)

def processString(data):
    sense.show_message(data["string"])
    time.sleep(1+len(data["string"])*0.1)

def processSeq(data):
    if "start" in data and len(data["start"])==64:
        sense.set_pixels(data["start"]);
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
        delay = min(1, step["delay"]) if "delay" in step else 0.1
        time.sleep(delay)
    time.sleep(2) # Hold final state
    sense.clear()
    time.sleep(1)

def formatMap(arr):
    # Detect 2d array vs flat array
    outmap = [[0,0,0]]*64
    two_d = None
    for index, i in enumerate(arr):
        if(len(i)>0):
            if isinstance(i[0],list):
                # This is a 2d arr
                if(two_d == False):return outmap;
                two_d = True;
                for innerindex, j in enumerate(i):
                    if(len(j)>0):
                        outmap[(8*index + innerindex)] = formatRGB(j)
            else:
                # Can't switch modes
                if(two_d == True):return outmap;
                two_d = False;
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
        logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                str(self.path), str(self.headers), post_data.decode('utf-8'))
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
