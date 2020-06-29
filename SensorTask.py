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

GUIAdress = './TMP/GUI_socket'
LoggerAdress = './TMP/Logger_socket'

GUI_sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)
Logger_sock = socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM)

try:
	GUI_sock.connect(GUIAdress)
	GUI_Task = True
	print('GUI connected')
except:
	print('GUI socket not connected')
	GUI_Task = False

try:
	Logger_sock.connect(LoggerAdress)
	Logger_Task = True
	print('Logger connected')
except:
	print('Logger socket no connected')
	Logger_Task = False



next_call = time.time()

def fxn():
	global next_call
	temperature = vcgm.measure_temp()
	temperature = str(temperature)
	timestemp = str(time.time())
	dict = {'timestemp':timestemp,'temperature':temperature}
	data_string = json.dumps(dict).encode('utf-8')
	if GUI_Task: GUI_sock.sendall(data_string)
	if Logger_Task: Logger_sock.sendall(data_string)
	next_call = next_call+0.1
	threading.Timer(next_call - time.time(), fxn).start()
fxn()
