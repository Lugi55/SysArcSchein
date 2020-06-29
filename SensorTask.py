from vcgencmd import Vcgencmd
import time
import threading
import os
import socket
import time
import json


niceValue = os.nice(-10)
print('niceValue:',niceValue)

vcgm = Vcgencmd()

serverAdress = './TMP/GUI_socket'

sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)

try:
	sock.connect(serverAdress)
	GUI_Task = True
	print('GUI connected')
except:
	print('GUI socket not connected')
	GUI_Task = False


next_call = time.time()

def fxn():
	global next_call
	temperature = vcgm.measure_temp()
	temperature = str(temperature)
	timestemp = str(time.time())
	dict = {'timestemp':timestemp,'temperature':temperature}
	data_string = json.dumps(dict).encode('utf-8')
	if GUI_Task: sock.sendall(data_string)
	next_call = next_call+0.1
	threading.Timer(next_call - time.time(), fxn).start()
fxn()
