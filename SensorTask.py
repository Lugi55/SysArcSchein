from IMU.lis3mdl import LIS3MDL
from IMU.lps25h import LPS25H
from IMU.lsm6ds33 import LSM6DS33
from vcgencmd import Vcgencmd
import paho.mqtt.client as paho
import logging
import os
import time
import json
import signal
import sys
import random

def main():
	#init logging module
	logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
	logging.info('SensorTask\t\tstart')

	#defien os priority
	niceValue = os.nice(10)
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
		self.client.message_callback_add('local/com2/car',self.on_com2car)
		self.client.message_callback_add('local/RFID',self.on_RFID)
		self.client.subscribe('local/#')
		self.client.loop_start()

		#init some sensor values
		self.humidity = 40
		self.speed = 0
		self.steeringAngle = 0
		self.LIDAR = 10

	def on_subscribe(self,client,userdata,mid,graned_qos):
		logging.info('SensorTask\t\tsubscribe to local/com2/car')

	def on_com2web(self,tokenID):
		dict = {
			"timestamp":time.time(),
			"tokenID":tokenID,
			"login":not self.login
			}
		self.client.publish('local/com2web',json.dumps(dict), qos = 2)
		print(dict)

	def on_RFID(self,client,userdata,msg):
		logging.info('SenosrTask\t\tRFID message incoming')
		dict = json.loads(msg.payload.decode('utf-8'))
		self.on_com2web(dict['tokenID'])

	def on_com2car(self,client,userdata,msg):
		logging.info('SensorTask\t\ttry user login or logout')
		dict = json.loads(msg.payload.decode('utf-8'))
		if self.login == False and dict["login"]==True and dict["certified"]==True:
			logging.info('SensorTask\t\tuser login succesfull')
			self.userName = dict["user"]["userName"]
			self.login = True
		if self.login == False and dict["login"]==False:
			logging.info('SensorTask\t\tno user to unlog')
		if self.login == False and dict["login"]==True and dict["certified"]==False:
			logging.info('SensorTask\t\tuser not certified')
		if self.login == True and dict["login"]==True:
			logging.info('SensorTask\t\ta user is already logined in')
		if self.login == True and dict["login"]==False and dict["user"]["userName"]==self.userName:
			logging.info('SensorTask\t\tuser logout succesfull')
			self.userName = None
			self.login = False


	def randomWalk(self,start,stop,dx,x):
		if not self.login: dx = dx*10
		if x<start:
			return x + random.uniform(-dx,0)
		if x>stop:
			return x + random.uniform(0,dx)
		else:
			return x + random.uniform(-1,1)

	def puplishAll(self):
		#dummy dict
		self.dict = {"SensorValue1":[],"SensorValue3":[]}
		#Temperature
		self.temp = self.vcgm.measure_temp()
		self.tempDict = {"name":"Temperature","timestamp":time.time(),"value":self.temp}
		#LIDAR
		self.LIDAR += self.randomWalk(start=5,stop=150,dx=0.5,x=self.LIDAR)
		self.LIDARDict = {"name":"LIDAR","timestamp":time.time(),"value":self.LIDAR}
		#Speed
		self.speed += self.randomWalk(start=0,stop=150,dx=0.5,x=self.speed)
		self.speedDict = {"name":"Speed","timestamp":time.time(),"value":self.speed}
		#SteeringAngle
		self.steeringAngle += self.randomWalk(start=5,stop=150,dx=0.5,x=self.steeringAngle)
		self.steeringAngleDict = {"name":"LIDAR","timestamp":time.time(),"value":self.steeringAngle}
		#Altimeter
		self.altimeter = self.lps25h.get_barometer_raw()
		self.altimeterDict = {"name":"Altimeter","timestamp":time.time(),"value":self.altimeter}
		#Humidity
		self.humidity = self.randomWalk(start=10,stop=95,dx=0.1,x=self.humidity)
		self.humidityDict = {"name":"Humidity","timestamp":time.time(),"value":self.humidity}
		#Acceleration
		self.accel = self.lsm6ds33.get_accelerometer_g_forces()
		self.accelDict = {"name":"Acceleration","timestamp":time.time(),"valueX":self.accel[0],"valueY":self.accel[1],"valueZ":self.accel[2]}
		#Gyro
		self.gyro = self.lsm6ds33.get_gyro_angular_velocity()
		self.gyroDict = {"name":"Gyro","timestamp":time.time(),"valueX":self.gyro[0],"valueY":self.gyro[1],"valueZ":self.gyro[2]}
		#Magnetometer
		self.mag = self.lis3mdl.get_magnetometer_raw()
		self.magDict = {"name":"Magnetometer","timestmap":time.time(),"valueX":self.mag[0],"valueY":self.mag[1],"valueZ":self.mag[2]}
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
		self.client.publish('local/sensor', json.dumps(self.dict), qos = 0)
		#when not login 1s measurement frequency
		self.next_call = self.next_call+0.1
		time.sleep(self.next_call - time.time())

	def puplishPart(self):
		#dummy dict
		self.dict = {"SensorValue1":[],"SensorValue3":[]}
		#Temperature
		self.temp = self.vcgm.measure_temp()
		self.tempDict = {"name":"Temperature","timestamp":time.time(),"value":self.temp}
		#Humidity
		self.humidity = self.randomWalk(start=10,stop=95,dx=0.1,x=self.humidity)
		self.humidityDict = {"name":"Humidity","timestamp":time.time(),"value":self.humidity}
		#Acceleration
		self.accel = self.lsm6ds33.get_accelerometer_g_forces()
		self.accelDict = {"name":"Acceleration","timestamp":time.time(),"valueX":self.accel[0],"valueY":self.accel[1],"valueZ":self.accel[2]}
		#Gyro
		self.gyro = self.lsm6ds33.get_gyro_angular_velocity()
		self.gyroDict = {"name":"Gyro","timestamp":time.time(),"valueX":self.gyro[0],"valueY":self.gyro[1],"valueZ":self.gyro[2]}
		#make big dict to publish
		self.dict["SensorValue1"].append(self.humidityDict)
		self.dict["SensorValue1"].append(self.tempDict)
		self.dict["SensorValue3"].append(self.accelDict)
		self.dict["SensorValue3"].append(self.gyroDict)
		#publish to local Brocker
		self.client.publish('local/sensor', json.dumps(self.dict), qos = 0)
		#when not login 1s measurement frequency
		self.next_call = self.next_call+1
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
