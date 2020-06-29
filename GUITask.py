import socket
import os
import time
import json
import cursor

HOST = '127.0.0.1'
PORT = 5002

niceValue = os.nice(10)
print('niceValue:',niceValue)


serverAdress = './TMP/GUI_socket'

try:
	os.unlink(serverAdress)
except:
	if os.path.exists(serverAdress):
		raise

sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sock.bind(serverAdress)
print('wait for socket connection')

os.system('clear')
cursor.hide()

def move(y,x):
	print('\033[%d;%dH' % (y,x))

while True:
	os.system('clear')
	print('Menu')
	print('start gui [y/n]')
	userInput = input()


	if userInput == 'y' or 'Y':
		os.system('clear')
		oldtime = 0
		drift = 0
		init = True
		run = True
		try:
			while True:
				data = sock.recv(1024)
				dict = json.loads(data.decode('utf-8'))
				dt = float(dict['timestemp'])-oldtime
				oldtime = float(dict['timestemp'])
				gitter = 0.1-dt
				drift += gitter
				if init:
					drift = 0
					gitter = 0
					dt = 0
					init = False
				move(1,1)
				print('temperature:\t %3.2f'%float(dict['temperature']))
				print('timestemp:\t %15.9f'%float(dict['timestemp']))
				print('dt:\t\t %1.9f'%dt)
				if gitter>0:
	 				print('gitter:\t\t %1.9f'%gitter)
				else:
					print('gitter:\t\t%1.9f'%gitter)
				if drift>0:
					print('drift:\t\t %1.9f'%drift)
				else:
					print('drift:\t\t%1.9f'%drift)
				print('\nto go back Ctrl+c')
		except KeyboardInterrupt:
			pass
