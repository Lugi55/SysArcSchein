from IMU.lis3mdl import LIS3MDL
from IMU.lps25h import LPS25H
from IMU.lsm6ds33 import LSM6DS33
from vcgencmd import Vcgencmd
from filelock import FileLock
import paho.mqtt.client as paho
import logging
import os
import time
import json
import signal
import sys
import random
import constants


def main():
	#init logging module
	logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
	logging.info('SensorTask\t\tstart')

	#defien os priority
	niceValue = os.nice(constants.SensorTaskNiceness)
	logging.info('SensorTask\t\tniceValue:%s',niceValue)

	#register signalHandler
	signal.signal(signal.SIGINT, signalHandler)

	mySensor = Sensor()
	mySensor.run()

class Sensor():
	def __init__(self):
		#login or not login
		self.login = False
		self.userName = None

		#Get hw sensor
		self.lis3mdl = LIS3MDL()
		self.lis3mdl.enable()
		self.lps25h = LPS25H()
		self.lps25h.enable()
		self.lsm6ds33 = LSM6DS33()
		self.lsm6ds33.enable()
		self.vcgm = Vcgencmd()
		self.next_call = time.time()

		#init MQTT Client
		self.client = paho.Client()
		self.client.connect(host='localhost',port=1883)
		self.client.on_subscribe = self.on_subscribe
		self.client.message_callback_add(constants.local_com2_car_topic,self.on_com2car)
		self.client.message_callback_add(constants.local_RFID_topic ,self.on_RFID)
		self.client.subscribe(constants.local_subscription)
		self.client.loop_start()

		#init some sensor values
		self.humidity = 40
		self.speed = 0
		self.steeringAngle = 0
		self.LIDAR = 10
		self.userLoginLogout()

	def on_subscribe(self,client,userdata,mid,graned_qos):
		logging.info('SensorTask\t\tsubscribe to local/com2/car')

	def on_com2web(self,tokenID):
		dict = {
			"timestamp":time.time(),
			"tokenID":tokenID,
			"login":not self.login
			}
		self.client.publish('local/com2/web',json.dumps(dict), qos = 2)
		print(dict)

	def on_RFID(self,client,userdata,msg):
		logging.info('SenosrTask\t\tRFID message incoming')
		dict = json.loads(msg.payload.decode('utf-8'))
		self.on_com2web(dict['tokenID'])

	def userLoginLogout(self,dict=None):
		logging.info('SensorTask\t\tuser.txt modified')
		with open("user.txt",'w') as file:
			if self.login:
				file.write(json.dumps(dict))
			else:
				file.write('')



	def on_com2car(self,client,userdata,msg):
		logging.info('SensorTask\t\ttry user login or logout')
		dict = json.loads(msg.payload.decode('utf-8'))
		if self.login == False and dict["login"]==True and dict["certified"]==True:
			logging.info('SensorTask\t\tuser login succesfull')
			self.login = True
			self.userLoginLogout(dict)
		elif self.login == True and dict["login"]==False and dict["certified"]==True:
			logging.info('SensorTask\t\tuser logout succesfull')
			self.login = False
			self.userLoginLogout(dict)
		else:
			logging.info('SensorTask\t\someting went wrong with login or logout')


	def randomWalk(self,start,stop,dx,x):
		if not self.login: dx = dx*10
		if x<start:
			return x + random.uniform(0,dx)
		if x>stop:
			return x + random.uniform(-dx,0)
		else:
			return x + random.uniform(-dx,dx)

	def puplishAll(self):
		#dummy dict
		self.dict = {"SensorValue1":[],"SensorValue3":[]}
		#Temperature
		self.temp = self.vcgm.measure_temp()
		self.tempDict = {"name":"Temperature","timestamp":round(time.time(),6),"value":round(self.temp,3)}
		#LIDAR
		self.LIDAR = self.randomWalk(start=5,stop=150,dx=0.5,x=self.LIDAR)
		self.LIDARDict = {"name":"LIDAR","timestamp":round(time.time(),6),"value":round(self.LIDAR,3)}
		#Speed
		self.speed = self.randomWalk(start=0,stop=150,dx=0.5,x=self.speed)
		self.speedDict = {"name":"Speed","timestamp":round(time.time(),6),"value":round(self.speed,3)}
		#SteeringAngle
		self.steeringAngle = self.randomWalk(start=5,stop=150,dx=0.5,x=self.steeringAngle)
		self.steeringAngleDict = {"name":"steeringAngle","timestamp":round(time.time(),6),"value":round(self.steeringAngle,3)}
		#Altimeter
		self.altimeter = self.lps25h.get_barometer_raw()
		self.altimeterDict = {"name":"Altimeter","timestamp":round(time.time(),6),"value":round(self.altimeter,3)}
		#Humidity
		self.humidity = self.randomWalk(start=10,stop=95,dx=0.1,x=self.humidity)
		self.humidityDict = {"name":"Humidity","timestamp":round(time.time(),6),"value":round(self.humidity,3)}
		#Acceleration
		self.accel = self.lsm6ds33.get_accelerometer_g_forces()
		self.accelDict = {"name":"Acceleration","timestamp":round(time.time(),6),"valueX":round(self.accel[0],3),"valueY":round(self.accel[1],3),"valueZ":round(self.accel[2],3)}
		#Gyro
		self.gyro = self.lsm6ds33.get_gyro_angular_velocity()
		self.gyroDict = {"name":"Gyro","timestamp":round(time.time(),6),"valueX":round(self.gyro[0],3),"valueY":round(self.gyro[1],3),"valueZ":round(self.gyro[2],3)}
		#Magnetometer
		self.mag = self.lis3mdl.get_magnetometer_raw()
		self.magDict = {"name":"Magnetometer","timestamp":round(time.time(),6),"valueX":round(self.mag[0],3),"valueY":round(self.mag[1],3),"valueZ":round(self.mag[2],3)}
		#make big dict to publish
		self.dict["SensorValue1"].append(self.humidityDict)
		self.dict["SensorValue1"].append(self.tempDict)
		self.dict["SensorValue1"].append(self.LIDARDict)
		self.dict["SensorValue1"].append(self.speedDict)
		self.dict["SensorValue1"].append(self.steeringAngleDict)
		self.dict["SensorValue1"].append(self.altimeterDict)
		self.dict["SensorValue3"].append(self.accelDict)
		self.dict["SensorValue3"].append(self.gyroDict)
		self.dict["SensorValue3"].append(self.magDict)
		#publish to local Brocker
		self.client.publish(constants.local_sensor_topic, json.dumps(self.dict), qos = 0)
		#when not login 1s measurement frequency
		self.next_call = self.next_call+constants.measurementPeriodLogin
		time.sleep(self.next_call - time.time())

	def puplishPart(self):
		#dummy dict
		self.dict = {"SensorValue1":[],"SensorValue3":[]}
		#Temperature
		self.temp = self.vcgm.measure_temp()
		self.tempDict = {"name":"Temperature","timestamp":round(time.time(),6),"value":round(self.temp,3)}
		#Humidity
		self.humidity = self.randomWalk(start=10,stop=95,dx=0.1,x=self.humidity)
		self.humidityDict = {"name":"Humidity","timestamp":round(time.time(),6),"value":round(self.humidity,3)}
		#Acceleration
		self.accel = self.lsm6ds33.get_accelerometer_g_forces()
		self.accelDict = {"name":"Acceleration","timestamp":round(time.time(),6),"valueX":round(self.accel[0],3),"valueY":round(self.accel[1],3),"valueZ":round(self.accel[2],3)}
		#Gyro
		self.gyro = self.lsm6ds33.get_gyro_angular_velocity()
		self.gyroDict = {"name":"Gyro","timestamp":round(time.time(),6),"valueX":round(self.gyro[0],3),"valueY":round(self.gyro[1],3),"valueZ":round(self.gyro[2],3)}
		#make big dict to publish
		self.dict["SensorValue1"].append(self.humidityDict)
		self.dict["SensorValue1"].append(self.tempDict)
		self.dict["SensorValue3"].append(self.accelDict)
		self.dict["SensorValue3"].append(self.gyroDict)
		#publish to local Brocker
		self.client.publish(constants.local_sensor_topic, json.dumps(self.dict), qos = 0)
		#when not login 1s measurement frequency
		self.next_call = self.next_call+constants.measurementPeriodLogout
		time.sleep(self.next_call - time.time())

	#measurement Loop
	def run(self):
		while True:
			if self.login:
				self.puplishAll()
			else:
				self.puplishPart()




#signal Handler (Ctrl+C)
def signalHandler(sig,frame):
	logging.info('SensorTask\t\tLoggerTask execution Ctrl+C')
	sys.exit(0)


main()
