import json
import socket
import os


niceValue = os.nice(0)
print('niceValue:',niceValue)

serverAdress = './TMP/Logger_socket'
LoggerFilePath = './LoggerFile'
LoggerFileName = 'Test'

try:
	os.unlink(serverAdress)
except:
	if os.path.exists(serverAdress):
		raise

sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sock.bind(serverAdress)
print('wait for socket connection')
file = open('Test','a')

while True:
	data = sock.recv(1024)
	dict = json.loads(data.decode('utf-8'))
	file.write(json.dumps(dict)+'\n')

