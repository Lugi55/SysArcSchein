import paho.mqtt.client as paho
import os
import time
import json
import curses
import sys
import logging



def GUI(stdscr):
	menu = ['View Sensor Data', 'View Temperautre Topic', 'Scoreboard', 'Exit']
	def updateMenu(current_row):
		for idx, element in enumerate(menu):
			if idx == current_row:
				stdscr.attron(curses.color_pair(1))
				stdscr.addstr(idx+1,1,element)
				stdscr.attroff(curses.color_pair(1))
			else:
				stdscr.addstr(idx+1,1,element)

	stdscr.clear()
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.curs_set(0)
	current_row=0
	updateMenu(current_row)
	while 1:
		key = stdscr.getch()
		if key == curses.KEY_UP and current_row > 0:
			current_row -= 1
		elif key == curses.KEY_DOWN and current_row < len(menu)-1:
			current_row += 1
		elif key == curses.KEY_ENTER or key in [10, 13]:
			if current_row == menu.index('Exit'):
				return 'Exit'
			if curren_row == menu.index('View Sensor Data')
				return 'View Sensor Data'
		updateMenu(current_row)



#init logging module
logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
logging.info('GUITask\t\tstart')

niceValue = os.nice(10)
logging.info('GUITask\t\tniceValue:%s',niceValue)


def on_subscribe(client, userdata, mid, granted_qos):
	logging.info('GUITask\t\tSubscribed to SensorTask')
def on_message(client, userdata, msg):
	dict = json.loads(msg.payload.decode('utf-8'))


#init MQTT Client
client = paho.Client()
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(host='localhost',port= 1883)
client.subscribe('SensorTask/Temperature', qos=0)

#start GUI blocking
reply = curses.wrapper(GUI)
print(print)
if(reply == '')
	pass
elseif()

client.loop_start()
bla bla
bla bla
client.loop_stop()


client.loop_forever()







