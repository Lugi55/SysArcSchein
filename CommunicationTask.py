import paho.mqtt.client as paho
import json
import os
import logging
import signal
import sys
import time
import threading
import queue
import constants


# class for internal communication
class InternCom:

	def __init__(self):
		self.__logger_function("object created")
		# open / ceate file for overflow notation
		self.__overflow_file = open('LoggerData/overflow.log','a')

	def end_client(self):
		self._client.loop_stop()
		self.__logger_function("client loop ended by user")

	def set_flag(self, flag):
		self.__flag = flag

	def init_mqtt_client(self):
		self._client = paho.Client()
		self._client.message_callback_add('SensorTask/Temperature', self._on_sensor_message)
		self._client.on_message = self._on_message
		self._client.on_subscribe = self._on_subscribe
		self._client.connect(host='localhost',port= 1883)
		self._client.subscribe('SensorTask/#', qos=0)
		self.__logger_function("start MQTT client")
		# NON bloking start of MQTT Client
		self._client.loop_start()
		# start loop function
		self.__on_loop()

	#callback funktions
	def _on_subscribe(self, client, userdata, mid, granted_qos):
		self.__logger_function("subscribed to /SensorTask")

	def _on_message(self, client, userdata, msg):
		# logg unexpected message
		self.__logger_function("unexpected message" + msg.payload.decode('utf-8'))

	def _on_sensor_message(self, client, userdata, msg):
		global _sensor_buf
		# blocking queque access
		_sensor_buf.put(json.loads(msg.payload.decode('utf-8')))
		# avoid race condition with threadlock
		with lock:
			length = _sensor_buf.qsize()
			print(length)
			if length >= constants.sensorBufferSize:
				# delete all elements in queue
				_sensor_buf.queue.clear()
				self.__overflow_file.write("deleted sensor messages = "+str(length)+"\n")
				self.__logger_function("buffer: deleted messages = "+str(length))

	def __on_loop(self):
		global _FINISH
		while True:
			if _FINISH:
				# exit if user ends skript
				break
			pass

	#logger prints
	def __logger_function(self, text):
		logging.info('CommunicationTask\tInternCom: '+text)
		print(text)


# class for external communication
class ExternCom:
	__host = 'localhost'
	__port = 1883
	__qos = 0
	__topic = 'V3/Test'

	def __init__(self):
		self.__logger_function("object created")
	
	def end_client(self):
		self._client.loop_stop()
		self.__logger_function("client loop ended by user")

	def init_mqtt_client(self):
		self._client = paho.Client()
		self._client.on_subscribe = self._on_subscribe
		self._clienton_publish = self._on_publish
		self._client.connect(host='localhost',port= 1883)
		self.__logger_function("start MQTT client_extern")
		# NON bloking start of MQTT Client
		self._client.loop_start()
		# start loop function
		self.__on_loop()

	#callback funktions
	def _on_subscribe(self, client, userdata, mid, granted_qos):
		self.__logger_function("subscribed to /SensorTask")
		print(dict)

	def _on_publish(self, client, userdata, result):
		print("data published")
	
	def __on_loop(self):
		global _FINISH, _sensor_buf
		while True:
			if _FINISH:
				# exit if user ends skript
				break	
			# non-bocking get elemtent from queue with timeout 		
			try:
				msg = _sensor_buf.get(block=False)
			except queue.Empty:
				# pass expected empty queue exception
				msg = None
				pass
			if msg is not None:
				# send message from buffer
				self._client.publish(self.__topic, str(msg), qos = self.__qos)
				#print(rc)
				# tell queue that task is done
				_sensor_buf.task_done()
			time.sleep(constants.measruementPeriodLogin / 10)

	#logger prints
	def __logger_function(self, text):
		logging.info('CommunicationTask\tExternCom: '+text)
		print(text)


#signal Handler (Ctrl+C)
def signalHandler(sig,frame):
	global com_intern, com_extern, t1, t2, _FINISH
	logging.info('CommunicationTask\tCtrl+C - killed by user')
	com_intern.end_client()
	com_extern.end_client()
	_FINISH = True
	t1.join()
	print("exit t1")
	t2.join()
	print("exit t2")




if __name__ == "__main__":
	#define os priority
	niceValue = os.nice(0)
	#init logging module
	logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
	logging.info('CommunicationTask\tniceValue:%s',niceValue)
	#register signalHandler
	signal.signal(signal.SIGINT, signalHandler)
	# create queues
	_sensor_buf = queue.Queue()
	# create communication objects
	com_intern = InternCom()
	com_extern = ExternCom()
	# use threads
	_FINISH = False
	lock = threading.Lock()
	t1 = threading.Thread(target=com_intern.init_mqtt_client)
	t2 = threading.Thread(target=com_extern.init_mqtt_client)

	t1.start()
	t2.start()

	# interpreter should not reach this area
	logging.info('CommunicationTask\tThreading error') 



