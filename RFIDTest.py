import paho.mqtt.client as paho
import json
import time
import os

while True:
	os.system('clear')
	print('Please Enter a RFID TokenID')
	tokenID = str(input())

	client = paho.Client()
	client.connect(host='localhost',port= 1883)
	client.loop_start()
	dict = {"tokenID":tokenID,}
	client.publish('local/RFID',json.dumps(dict),qos=0)




