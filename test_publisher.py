import paho.mqtt.client as paho
from vcgencmd import Vcgencmd
import time
import json
import signal
import sys

# This script publishes and listen at the same time 
# for testing

send_static_test_msg = True
test_gui_and_comm_task = True

test_msg = {   "SensorValue1":[      {
	   "name":"Humidity",
	   "timestamp":1595018177.2537384,
	   "value":62.3947692431115

},
	{
	   "name":"Temperature",
	   "timestamp":1595018177.253633,
	   "value":53.7

}

],
   "SensorValue3":[      {
	   "name":"Acceleration",
	   "timestamp":1595018177.258011,
	   "valueX":-0.13847,
	   "valueY":0.993202,
	   "valueZ":-0.082228

},
	{
	   "name":"Gyro",
	   "timestamp":1595018177.2622058,
	   "valueX":2.205,
	   "valueY":-5.845,
	   "valueZ":-3.115

}

]
}


def main():
	global test_msg, send_static_test_msg, test_gui_and_comm_task

	def on_publish(client, userdata, result):
		print("data published")
	def on_message(client, userdata, msg):
		dict = json.loads(msg.payload.decode('utf-8'))
		print(dict)

	#signal Handler (Ctrl+C)
	def signalHandler(sig,frame):
		client.loop_stop()
		print("user stopped process")
		sys.exit(0)
	
	if test_gui_and_comm_task:
		host = 'localhost'
		port = 1883
	else:
		host = '192.168.200.165'
		port = 8883
	
	qos = 2
	topic = '/SysArch/V3/sensor'

	#register signalHandler
	signal.signal(signal.SIGINT, signalHandler)
	# cpu temperature
	vcgm = Vcgencmd()
	#init MQTT Client
	client = paho.Client()
	# username and password
	client.username_pw_set(username="V3", password="DE5")
	# connect to broker
	client.connect(host=host,port=port,keepalive=60)
	client.on_publish = on_publish
	client.on_message = on_message
	# subscribe
	client.subscribe(topic, qos=qos)
	client.loop_start() # for qos 1, 2 and subscription
	

	#measurement Loop
	while True:
		temperature = str(vcgm.measure_temp())
		timestamp = str(time.time())
		if send_static_test_msg:
			dict = test_msg
		else:
			dict = {'timestamp':timestamp,'temperature':temperature}
		# publish
		if test_gui_and_comm_task:
			client.publish("/SysArch/V3/com2/car", json.dumps(dict), qos = 2)
			client.publish("local/com2/web", json.dumps(dict), qos = 2)
			client.publish("local/sensor",  json.dumps(dict), qos = 0)
		else:
			client.publish(topic, json.dumps(dict), qos = qos)
		time.sleep(0.5)


main()
