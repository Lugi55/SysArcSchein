from vcgencmd import Vcgencmd
import paho.mqtt.client as paho
import logging
import os
import time
import json
import signal
import sys

def main():
	#init logging module
	logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
	logging.info('SensorTask\t\tstart')

	#defien os priority
	niceValue = os.nice(10)
	logging.info('SensorTask\t\tniceValue:%s',niceValue)

	#init MQTT Client
	client = paho.Client()
	client.connect(host='localhost',port=1883)
	client.loop_start()
	vcgm = Vcgencmd()
	next_call = time.time()

	#register signalHandler
	signal.signal(signal.SIGINT, signalHandler)

	#measurement Loop
	while True:
		temperature = vcgm.measure_temp()
		temperature = str(temperature)
		timestamp = str(time.time())
		dict = {'timestamp':timestamp,'temperature':temperature}
		client.publish('SensorTask/Temperature', json.dumps(dict), qos = 0)
		next_call = next_call+0.1
		time.sleep(next_call - time.time())


#signal Handler (Ctrl+C)
def signalHandler(sig,frame):
	logging.info('SensorTask\t\tLoggerTask execution Ctrl+C')
	sys.exit(0)


main()
