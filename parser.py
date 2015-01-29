import time
import picamera
import serial
import RPi.GPIO as GPIO
import base64
import numpy as np
import math
import cv2
import os
import sys
import string
import re
from PIL import Image

symbols=75
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(26,GPIO.OUT)
xbee=serial.Serial('/dev/ttyUSB0', 115200) #, parity=serial.PARITY_ODD, stopbits=1)
ardu=serial.Serial('/dev/ttyACM0', 115200, timeout=None) #0 is non-blocking mode (not a good idea)
if (xbee.isOpen() ==  False):
    xbee.open()
xbee.flushInput()
xbee.flushOutput()
if (ardu.isOpen() ==  False):
    ardu.open()
ardu.flushInput()
ardu.flushOutput()
time.sleep(1) #because python lies

# functions
def processRappelCmd(cmd):
    print 'weeeeeeee'
    ardu.write(cmd)
    while ardu.inWaiting() < 1:
        time.sleep(0.1)
    print 'got reply'
    reply = ardu.readline()
    if reply[0] == '$':
        xbee.write(reply)
        print 'sent reply'

def processImageCmd(cmd):
    print 'aww snap'
    GPIO.output(26,True)
    with picamera.PiCamera() as camera:
        #camera.resolution=(2592,1944)
        camera.resolution=(1280,720)
        location='/home/pi/parser/Pics/testPic.jpg'
        #location2='/home/pi/parser/Pics/testPic2.jpg'
        location3='/home/pi/parser/Pics/testPic3.jpg'
        camera.capture(location)
        #im=Image.open(location)
        #im2=im.resize((1280,720),Image.ANTIALIAS)
        #im2.save(location2)
        im3=cv2.imread(location)
        cv2.imwrite(location3,im3,[int(cv2.IMWRITE_JPEG_QUALITY),50])
        with open(location3,'rb') as image_file:
            encodStr=base64.b64encode(image_file.read())
            image_file.close()
        picLength=len(encodStr)
        numIt=picLength/symbols
        xbee.write("$I")
        for i in range(0, numIt):
            xbee.write(encodStr[i*symbols:(i+1)*symbols])
            time.sleep(0.03)
        xbee.write(encodStr[(i+1)*symbols:])
        xbee.write('ENDOFFILE\n')
    GPIO.output(26,False)

def processDriveCmd(cmd):
    print 'vroom vroom'
    ardu.write(cmd)
    while ardu.inWaiting() < 1:
        time.sleep(0.1)
    reply = ardu.readline()
    if reply[0] == '$':
        xbee.write(reply)

def processStatusCmd(cmd):
    print 'ohai'
    ardu.write(cmd)
    while ardu.inWaiting() < 1:
        time.sleep(0.1)
    reply = ardu.readline()
    if reply[0] == '$':
        xbee.write(reply)
# end of functions

# main loop
while True:
    while xbee.inWaiting() < 1:
        time.sleep(0.1)
    xbeeIn = xbee.readline()
    if xbeeIn[0] == '$':
        cmdType = xbeeIn[1]
        if cmdType == 'R':
            processRappelCmd(xbeeIn)
        elif cmdType == 'I':
            processImageCmd(xbeeIn)
        elif cmdType == 'D':
            processDriveCmd(xbeeIn)
        elif cmdType == 'S':
            processStatusCmd(xbeeIn)
        else:
            print 'you done goofed'
# end of main loop
