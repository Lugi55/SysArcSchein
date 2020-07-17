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
		self._client.message_callback_add('local/sensor', self._on_sensor_message)
		self._client.message_callback_add('local/con2/web', self._on_con2_web)
		self._client.message_callback_add('local/con2/car', self._do_nothing)
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

	def _on_con2_web(self, client, userdata, msg):
		global _con2_web_buf
		try:
			# blocking queque access
			_con2_web_buf.put(json.loads(msg.payload.decode('utf-8')))
		except queue.Full:
			with lock:
				_con2_car_buf.queue.clear()
			self.__logger_function("con2_car_overflow")
		# debug
		with lock:
			length = _con2_web_buf.qsize()
			print("con2_web " +str(length))

	def __on_loop(self):
		global _FINISH, _con2_car_buf
		while True:
			if _FINISH:
				# exit if user ends skript
				break
		    ############
			# con2/car #
			############	
			try:
				con_msg = _con2_car_buf.get(block=False)
			except queue.Empty:
				# pass expected empty queue exception
				con_msg = None
				pass
			if con_msg is not None:
				# send message from buffer
				self._client.publish("local/con2/car", str(con_msg), qos = 2)
				#print(rc)
				# tell queue that task is done
				_con2_car_buf.task_done()
			# sleep
			time.sleep(constants.measruementPeriodLogin / 10)

	#logger prints
	def __logger_function(self, text):
		logging.info('CommunicationTask\tInternCom: '+text)
		print(text)


# class for external communication
class ExternCom:
	__host = 'localhost'
	__port = 1883
	#__qos = 0
	#__topic = 'V3/sensor'

	def __init__(self):
		self.__logger_function("object created")
	
	def end_client(self):
		self._client.loop_stop()
		self.__logger_function("client loop ended by user")

	def init_mqtt_client(self):
		self._client = paho.Client()
		self._client.message_callback_add('V3/con2/car', self._on_con2_car)
		self._client.message_callback_add('V3/con2/web', self._do_nothing)
		self._client.message_callback_add('V3/sensor', self._do_nothing)
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

	def _on_con2_car(self, client, userdata, msg):
		global _con2_car_buf
		try:
			# blocking queque access
			_con2_car_buf.put(json.loads(msg.payload.decode('utf-8')))
		except queue.Full:
			with lock:
				_con2_car_buf.queue.clear()
			self.__logger_function("con2_car_overflow")
		# debug
		with lock:
			length = _con2_car_buf.qsize()
			print("con2_car " +str(length))
	
	def __on_loop(self):
		global _FINISH, _sensor_buf, _con2_web_buf
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
				self._client.publish("V3/sensor", str(sensor_msg), qos = 0)
				# tell queue that task is done
				_sensor_buf.task_done()
		    ############
			# con2/web #
			############	
			try:
				con_msg = _con2_web_buf.get(block=False)
			except queue.Empty:
				# pass expected empty queue exception
				con_msg = None
				pass
			if con_msg is not None:
				# send message from buffer
				self._client.publish("V3/con2/web", str(con_msg), qos = 2)
				#print(rc)
				# tell queue that task is done
				_con2_web_buf.task_done()
			# sleep
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
	_con2_web_buf = queue.Queue()
	_con2_car_buf = queue.Queue()
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



