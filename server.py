#!/usr/bin/env python
# -*- coding: utf8 -*-
#
# Copyright (c) 2013 Baptiste LABAT
#
# Licensed under the MIT License,
# https://github.com/baptistelabat/robokite
# Authors: Baptiste LABAT
#
# Used http://www.linuxforu.com/2012/04/getting-started-with-html5-websockets/
 
import tornado.web
import tornado.websocket
import tornado.ioloop
import os
import datetime
import time
import json
import math

clients = []
global t0
global ser
t0 = time.time()
import serial

def openSerial():
  global ser
  
  # Loop over varying serial port till you find one (assume you have only one device connected)
  locations = ['/dev/ttyACM0','/dev/ttyACM1','/dev/ttyACM2','/dev/ttyACM3','/dev/ttyACM4','/dev/ttyACM5','/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3','/dev/ttyS0','/dev/ttyS1','/dev/ttyS2','/dev/ttyS3','COM0','COM1','COM2','COM3','COM4','COM5','COM6']
  for device in locations:
    try:
      print("Trying...",device)
      ser = serial.Serial(device, baudrate=19200, timeout=1)
      print("Connected on ", device)
      time.sleep(1.5) # Arduino is reset when opening port so wait before communicating
      # An alternative would be to listen to a message from the arduino saying it is ready
      ser.write('i1') # i to start serial control, 1 is the minimum expecting message frequency (in house protocol)

      break
    except:
      print("Failed to connect on ", device)
      

def checkSerial():
    global ser
    global serialPending
    global t0
    t = time.time()-t0 
    try:
        s = ser.readline().decode('utf8')
        print("Received from arduino: " + s)
    except Exception as e:
        print("Error reading from serial port" + str(e))
        openSerial()
        d = str(-512)   
        s = d+', ' + d + ', ' + d + ', ' +d + ', '+d+', '+d
    if len(s):
      a = s.split(',') 
      print( a)     
      for c in clients:
        c.write_message( json.dumps({'x':t, 'd0':float(a[0]), 'd1':float(a[1]), 'd2':float(a[2]), 'd3':float(a[3]), 'd4':float(a[4]), 'd5':float(a[5])}))

        
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("graph.html")
 
class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def on_message(self, message):  
      print("message received"  )   

    def open(self):
      clients.append(self)
      self.write_message(u"Connected")
      print( "open")
      
    def on_close(self):
      clients.remove(self)
      print ("close")

handlers = [
    (r"/", MainHandler),
    (r"/websocket", WebSocketHandler),
]
settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "static"),
)
application = tornado.web.Application(handlers, **settings)

def timer():
    global t0
    for c in clients:
        #c.write_message(datetime.datetime.utcnow().strftime("%Y%m%d_%Hh%Mm_%Ss"))
        t = time.time()-t0
        c.write_message( json.dumps({'x':t, 'y':500+500*math.sin(t)})
)
 
if __name__ == "__main__":
    openSerial()
    application.listen(8080)
    mainLoop = tornado.ioloop.IOLoop.instance()
    #scheduler = tornado.ioloop.PeriodicCallback(timer, 100, io_loop = mainLoop)
    scheduler = tornado.ioloop.PeriodicCallback(checkSerial, 1)
    scheduler.start()
    mainLoop.start()
    

