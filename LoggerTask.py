import paho.mqtt.client as paho
import datetime
import json
import socket
import os
import logging
import signal
import sys


def main():
<<<<<<< HEAD
=======
	#new Logger File
	def createNewLoggerFile():
		now = datetime.datetime.now()
		fileName = now.strftime("%Y-%m-%d_%H:%M:%S.log")
		fileName = 'LoggerData/'+fileName
		file = open(fileName,'a')
		return file

	#callback funktions
	def on_subscribe(client, userdata, mid, granted_qos):
		logging.info('LoggerTask\t\Subscribed to SensorTask')
	def on_message(client, userdata, msg):
		global file
		global currentNumberOfLogs
		currentNumberOfLogs += 1
		if currentNumberOfLogs > numberOfLogsPerFile:
			file = createNewLoggerFile()
			logging.info('LoggerTask\t\tnew Log file has been created')
	def on_temperature_message(client, userdata, msg):
		dict = json.loads(msg.payload.decode('utf-8'))
		file.write(json.dumps(dict)+'\n')


>>>>>>> 6ca9c467f7b610e0f677f69707fb04ddb09e073b
	#init logging module
	logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
	logging.info('LoggerTask\t\tstart')

	#define os priority
	niceValue = os.nice(0)
	logging.info('LoggerTask\t\tniceValue:%s',niceValue)

	#register signalHandler
	signal.signal(signal.SIGINT, signalHandler)

<<<<<<< HEAD
	#get Object
	myLogger = Logger()
	myLogger.start_MQTT()


class Logger():
	def __init__(self):

		#init first file
		self.createNewLoggerFile()

		#init MQTT Client
		self.client = paho.Client()
		self.client.message_callback_add('SensorTask/Temperature', self.on_temperature_message)
		self.client.on_message = self.on_message
		self.client.on_subscribe = self.on_subscribe
		self.client.connect(host='localhost',port= 1883)
		self.client.subscribe('SensorTask/#', qos=0)


	#new Logger File
	def createNewLoggerFile(self):
		self.fileName = datetime.datetime.now().strftime("%Y-%m-%d_%H.log")
		self.fileName = 'LoggerData/'+self.fileName
		self.file = open(self.fileName,'a')

	#callback funktions
	def on_subscribe(self, client, userdata, mid, granted_qos):
		logging.info('LoggerTask\t\tSubscribed to SensorTask')

	def on_message(self, client, userdata, msg):
		if currentFileTime < datetime.datetime.now()-datetime.timedelta(hours=1):
			currentFileTime = datetime.datetime.now()
			createNewLoggerFile()
			logging.info('LoggerTask\t\tnew Log file has been created')
=======
	#define LoggerFile size
	numberOfLogsPerFile = 100000
	currentNumberOfLogs = 0
>>>>>>> 6ca9c467f7b610e0f677f69707fb04ddb09e073b

	def on_temperature_message(self, client, userdata, msg):
		self.dict = json.loads(msg.payload.decode('utf-8'))
		self.file.write(json.dumps(self.dict)+'\n')

	def start_MQTT(self):
		self.client.loop_forever()



#signal Handler (Ctrl+C)
def signalHandler(sig,frame):
	logging.info('LoggerTask\t\tCtrl+C')
	sys.exit(0)


main()
