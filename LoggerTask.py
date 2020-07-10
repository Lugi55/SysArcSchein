import paho.mqtt.client as paho
import datetime
import json
import socket
import os
import logging
import signal
import sys

def main():
	#init logging module
	logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
	logging.info('LoggerTask\t\tstart')

	#define os priority
	niceValue = os.nice(0)
	logging.info('LoggerTask\t\tniceValue:%s',niceValue)

	#register signalHandler
	signal.signal(signal.SIGINT, signalHandler)

	#get Object
	myLogger = Logger()
	myLogger.start_MQTT()


class Logger():
	def __init__(self):

		#init first file
		self.createNewLoggerFile()

		#init MQTT Client
		self.client = paho.Client()
		self.client.on_message = self.on_message
		self.client.on_subscribe = self.on_subscribe
		self.client.connect(host='localhost',port= 1883)
		self.client.subscribe('SensorTask', qos=0)
		#create first fileTime
		self.currentFileTime = datetime.datetime.now().replace(microsecond=0,second=0,minute=0)

	#new Logger File
	def createNewLoggerFile(self):
		self.fileName = datetime.datetime.now().replace(microsecond=0, second=0, minute=0).strftime("%Y-%m-%d_%H.log")
		self.fileName = 'LoggerData/'+self.fileName
		self.file = open(self.fileName,'a')

	#callback funktions
	def on_subscribe(self, client, userdata, mid, granted_qos):
		logging.info('LoggerTask\t\tSubscribed to SensorTask')

	def on_message(self, client, userdata, msg):
		if not( self.currentFileTime == datetime.datetime.now().replace(microsecond=0,second=0,minute=0)):
			self.currentFileTime = datetime.datetime.now()
			self.createNewLoggerFile()
			logging.info('LoggerTask\t\tnew Log file has been created')
		self.dict = json.loads(msg.payload.decode('utf-8'))
		self.file.write(json.dumps(self.dict)+'\n')

	def start_MQTT(self):
		self.client.loop_forever()


#signal Handler (Ctrl+C)
def signalHandler(sig,frame):
	logging.info('LoggerTask\t\tCtrl+C')
	sys.exit(0)


main()
