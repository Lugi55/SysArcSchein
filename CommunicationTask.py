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
	__host = 'localhost'
	__port = 1883
	__com2_car_topic = 'local/com2/car'
	__com2_web_topic = 'local/com2/web'
	__sensor_topic = 'local/sensor'

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
		self._client.message_callback_add(self.__sensor_topic, self._on_sensor_message)
		self._client.message_callback_add(self.__com2_web_topic, self._on_com2_web)
		self._client.message_callback_add(self.__com2_car_topic, self._do_nothing)
		self._client.on_message = self._on_message
		self._client.on_subscribe = self._on_subscribe
		self._client.connect(host=self.__host,port=self.__port)
		self._client.subscribe(topic='local/#')
		self.__logger_function("start MQTT client")
		# NON bloking start of MQTT Client
		self._client.loop_start()
		# start loop function
		self.__on_loop()

	#callback funktions
	def _on_subscribe(self, client, userdata, mid, granted_qos):
		self.__logger_function("subscribed")

	def _on_message(self, client, userdata, msg):
		# logg unexpected message
		self.__logger_function("unexpected message" + msg.payload.decode('utf-8'))

	def _do_nothing(self, client, userdata, msg):
		pass

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

	def _on_com2_web(self, client, userdata, msg):
		global _com2_web_buf
		try:
			# blocking queque access
			_com2_web_buf.put(json.loads(msg.payload.decode('utf-8')))
		except queue.Full:
			with lock:
				_com2_car_buf.queue.clear()
			self.__logger_function("com2_car_overflow")
		# debug
		with lock:
			length = _com2_web_buf.qsize()
			print("com2_web " +str(length))

	def __on_loop(self):
		global _FINISH, _com2_car_buf
		while True:
			if _FINISH:
				# exit if user ends skript
				break
		    ############
			# com2/car #
			############	
			try:
				com_msg = _com2_car_buf.get(block=False)
			except queue.Empty:
				# pass expected empty queue exception
				com_msg = None
				pass
			if com_msg is not None:
				# send message from buffer
				self._client.publish(self.__com2_car_topic, str(com_msg), qos = 2)
				#print(rc)
				# tell queue that task is done
				_com2_car_buf.task_done()
			# sleep
			#time.sleep(constants.measruementPeriodLogin / 10)
			time.sleep(0.01)

	#logger prints
	def __logger_function(self, text):
		logging.info('CommunicationTask\tInternCom: '+text)
		print(text)


# class for external communication
class ExternCom:
	#__host = 'localhost'
	#__port = 1883
	__host = '192.168.200.165'
	__port = 8883
	__com2_car_topic = '/SysArch/V3/com2/car'
	__com2_web_topic = '/SysArch/V3/com2/web'
	__sensor_topic = '/SysArch/V3/sensor'
	__user = 'V3'
	__password = 'DE5'

	def __init__(self):
		self.__logger_function("object created")
	
	def end_client(self):
		self._client.loop_stop()
		self.__logger_function("client loop ended by user")

	def init_mqtt_client(self):
		self._client = paho.Client()
		# username and password
		self._client.username_pw_set(username=self.__user, password=self.__password)
		self._client.message_callback_add(self.__com2_car_topic, self._on_com2_car)
		self._client.message_callback_add(self.__com2_web_topic, self._do_nothing)
		self._client.message_callback_add(self.__sensor_topic, self._do_nothing)
		self._client.on_message = self._on_message
		self._client.on_subscribe = self._on_subscribe
		self._clienton_publish = self._on_publish
		self._client.connect(host=self.__host,port=self.__port)
		self._client.subscribe('V3/#', qos=2)
		self.__logger_function("start MQTT client_extern")
		# NON bloking start of MQTT Client
		self._client.loop_start()
		# start loop function
		self.__on_loop()

	#callback funktions
	def _on_subscribe(self, client, userdata, mid, granted_qos):
		self.__logger_function("subscribed")
		print(dict)

	def _on_publish(self, client, userdata, result):
		print("data published")

	def _on_message(self, client, userdata, msg):
		# logg unexpected message
		self.__logger_function("unexpected message" + msg.payload.decode('utf-8'))

	def _do_nothing(self, client, userdata, msg):
		pass

	def _on_com2_car(self, client, userdata, msg):
		global _com2_car_buf
		try:
			# blocking queque access
			_com2_car_buf.put(json.loads(msg.payload.decode('utf-8')))
		except queue.Full:
			with lock:
				_com2_car_buf.queue.clear()
			self.__logger_function("com2_car_overflow")
		# debug
		with lock:
			length = _com2_car_buf.qsize()
			print("com2_car " +str(length))
	
	def __on_loop(self):
		global _FINISH, _sensor_buf, _com2_web_buf
		while True:
			if _FINISH:
				# exit if user ends skript
				break
			##########
			# sensor #
			##########	
			# non-bocking get elemtent from queue with timeout 		
			try:
				sensor_msg = _sensor_buf.get(block=False)
			except queue.Empty:
				# pass expected empty queue exception
				sensor_msg = None
				pass
			if sensor_msg is not None:
				# send message from buffer
				self._client.publish(self.__sensor_topic, str(sensor_msg), qos = 0)
				# tell queue that task is done
				_sensor_buf.task_done()
		    ############
			# com2/web #
			############	
			try:
				com_msg = _com2_web_buf.get(block=False)
			except queue.Empty:
				# pass expected empty queue exception
				com_msg = None
				pass
			if com_msg is not None:
				# send message from buffer
				self._client.publish(self.__com2_web_topic, str(com_msg), qos = 2)
				#print(rc)
				# tell queue that task is done
				_com2_web_buf.task_done()
			# sleep
			#time.sleep(constants.measruementPeriodLogin / 10)
			time.sleep(0.01)

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
	_com2_web_buf = queue.Queue(10) # maxsize = 10
	_com2_car_buf = queue.Queue(10) # maxsize = 10
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



