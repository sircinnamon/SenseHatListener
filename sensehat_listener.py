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
        if "board" in data:
            if(len(data["board"])!=64):
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
    sense.set_pixels(data["board"]);
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
    for pixel in data["sequence"]:
        if "colour" not in pixel:
            pixel["colour"] = (0,0,0)
        if "x" not in pixel: pixel["x"] = 0
        if "y" not in pixel: pixel["y"] = 0
        sense.set_pixel(pixel["x"], pixel["y"], pixel["colour"])
        time.sleep(0.1)
    time.sleep(2)
    sense.clear()
    time.sleep(1)

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
