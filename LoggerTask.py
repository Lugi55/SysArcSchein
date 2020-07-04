import paho.mqtt.client as paho
import datetime
import json
import socket
import os
import logging
import signal
import sys


def main():
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
		if currenNumberOfLogs > numberOfLogsPerFile:
			file = createNewLoggerFile()
			logging.info('LoggerTask\t\tnew Log file has been created')
	def on_temperature_message(client, userdata, msg):
		dict = json.loads(msg.payload.decode('utf-8'))
		file.write(json.dumps(dict)+'\n')


	#init logging module
	logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
	logging.info('LoggerTask\t\tstart')

	#define os priority
	niceValue = os.nice(0)
	logging.info('LoggerTask\t\tniceValue:%s',niceValue)

	#register signalHandler
	signal.signal(signal.SIGINT, signalHandler)

	#define LoggerFile size
	numberOfLogsPerFile = 100000;
	currentNumberOfLogs = 0;

	#init first file
	file = createNewLoggerFile()

	#init MQTT Client
	client = paho.Client()
	client.message_callback_add('SensorTask/Temperature', on_temperature_message)
	client.on_message = on_message
	client.on_subscribe = on_subscribe
	client.connect(host='localhost',port= 1883)
	client.subscribe('SensorTask/#', qos=0)

	#non bloking start of MQTT Client
	client.loop_forever()


#signal Handler (Ctrl+C)
def signalHandler(sig,frame):
	logging.info('LoggerTask\t\tCtrl+C')
	sys.exit(0)


main()
