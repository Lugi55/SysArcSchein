import paho.mqtt.client as paho
import json
import os
import logging
import signal
import sys
import time
import threading
import queue



# class for internal communication
class InternCom:
	# sensor message buffer
	__BUFFERLEN = 20
	__buffer = []

	def __init__(self):
		self.__logger_function("object created")
		# open / ceate file for overflow notation
		self.__overflow_file = open('LoggerData/overflow.log','a')

	def end_client(self):
		self._client.loop_stop()
		self.__logger_function("client loop ended by user")

	def get_buffer_element(self):
		# lock threads
		with lock:
			return self.__buffer.pop(0)

	def get_buffer_len(self):
		# lock threads
		with lock:
			return len(self.__buffer)	

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
		# lock threads 
		with lock:
			self.__buffer.append(json.loads(msg.payload.decode('utf-8')))
			#print(self.__buffer[-1]) # debug
			print ("buffer length: "+str(len(self.__buffer)))
			
			# if buffer overflows
			if len(self.__buffer) >= self.__BUFFERLEN:
				length = len(self.__buffer)
				# delete buffer content
				del self.__buffer[:]
				self.__overflow_file.write("deleted sensor messages = "+str(length)+"\n")
				self.__logger_function("buffer: deleted messages = "+str(length))


	def __on_loop(self):
		global _FINISH
		while True:
			if _FINISH:
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

	def set_interncom_obj(self, com_intern):
		self.__com_intern = com_intern

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
		global _FINISH
		while True:
			if _FINISH:
				break			
			if com_intern.get_buffer_len():
				# send message from buffer
				self._client.publish(self.__topic, str(self.__com_intern.get_buffer_element()), qos = self.__qos)
				#print(rc)
			time.sleep(0.1) # this value is chosen to overflow the buffer on purpose

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
	t2.join()



if __name__ == "__main__":
	#define os priority
	niceValue = os.nice(0)
	#init logging module
	logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
	logging.info('CommunicationTask\tniceValue:%s',niceValue)
	#register signalHandler
	signal.signal(signal.SIGINT, signalHandler)
	# create communication objects
	com_intern = InternCom()
	com_extern = ExternCom()
	com_extern.set_interncom_obj(com_intern)
	# use threads
	_FINISH = False
	lock = threading.Lock()
	t1 = threading.Thread(target=com_intern.init_mqtt_client)
	t2 = threading.Thread(target=com_extern.init_mqtt_client)

	t1.start()
	t2.start()

	# interpreter should not reach this area
	logging.info('CommunicationTask\tThreading error') 



