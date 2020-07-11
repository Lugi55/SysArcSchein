import paho.mqtt.client as paho
from vcgencmd import Vcgencmd
import time
import json
import signal
import sys

# This script publishes and listen at the same time 
# for testing

def main():

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

    host = 'localhost'
    port = 1883
    qos = 2
    topic = 'V3/Test'

    #register signalHandler
    signal.signal(signal.SIGINT, signalHandler)
    # cpu temperature
    vcgm = Vcgencmd()

    #init MQTT Client
    client = paho.Client()
    # connect to broker
    client.connect(host=host,port=port,keepalive=60)
    client.on_publish = on_publish
    client.on_message = on_message
    # subscribe
    client.subscribe(topic, qos=qos)
    # username and password
    #client.username_pw_set(username="V3", password="DE5")
    client.loop_start() # for qos 1, 2 and subscription
    

    #measurement Loop
    while True:
        temperature = vcgm.measure_temp()
        temperature = str(temperature)
        timestamp = str(time.time())
        dict = {'timestamp':timestamp,'temperature':temperature}
        # publish
        rc = client.publish(topic, json.dumps(dict), qos = qos)
        print(rc)
        time.sleep(0.5)


main()