#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#    Copyright 2014,2018 Mario Gomez <mario.gomez@teubi.co>
#
#    This file is part of MFRC522-Python
#    MFRC522-Python is a simple Python implementation for
#    the MFRC522 NFC Card Reader for the Raspberry Pi.
#
#    MFRC522-Python is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    MFRC522-Python is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with MFRC522-Python.  If not, see <http://www.gnu.org/licenses/>.
#

import paho.mqtt.client as paho
import json
import RPi.GPIO as GPIO
import MFRC522
import signal
import constants
import sys
import time

continue_reading = True

client = paho.Client()
client.connect(host='localhost',port= 1883)
client.loop_start()


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
	global continue_reading
	print "Ctrl+C captured, ending read."
	continue_reading = False
	GPIO.cleanup()
	sys.exit()

# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print "Welcome to the MFRC522 data read example"
print "Press Ctrl-C to stop."

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
	# Scan for cards
	(status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
	# If a card is found
	if status == MIFAREReader.MI_OK:
		print "Card detected"
	# Get the UID of the card
	(status,uid) = MIFAREReader.MFRC522_Anticoll()

	# If we have the UID, continue
	if status == MIFAREReader.MI_OK:
		ID = str(uid[0])+str(uid[1])+str(uid[2])+str(uid[3])
		# Print UID
		dict = {"tokenID":ID}
	client.publish('local/RFID',json.dumps(dict),qos=2)
		print "Card read UID: %s" % (ID)
		time.sleep(constants.RFIDTimeout)
