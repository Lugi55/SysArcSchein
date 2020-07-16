import paho.mqtt.client as paho
import os
import time
import json
import curses
from curses import textpad
import sys
import logging
import getch


menu = None
parent = [] 
disp = 0
last_stamp = 0 
drift = 0 
drift_flag = False
format_param = '{:016.6f}'

def GUI(stdscr):
	time_parent = 0
	global menu, menu_data

	if not menu:
		menu = menu_data
	
	def updateMenu(current_row, menu_var, parent_var=None):
		global menu
		if menu != menu_var:
			menu = menu_var
			current_row = 0
		if parent_var:
			global parent
			parent.append(parent_var)

		stdscr.clear()
		stdscr.addstr(1,2, menu['title'], curses.A_UNDERLINE) # Title for this menu
		stdscr.addstr(3,2, menu['subtitle'], curses.A_BOLD) #Subtitle for this menu
		for idx in range(len(menu_var['options'])):
			if idx == current_row:
				# print line with cursor
				stdscr.attron(curses.color_pair(1))
				stdscr.addstr(idx+4,4,'%d - %s' % (idx+1, menu_var['options'][idx]['title']))
				stdscr.attroff(curses.color_pair(1))
			else:
				# print other lines
				stdscr.addstr(idx+4,4,'%d - %s' % (idx+1, menu_var['options'][idx]['title']))

	stdscr.clear()
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.curs_set(0)
	current_row=0
	updateMenu(current_row, menu)


	while 1:
		key = stdscr.getch()
		if key == curses.KEY_UP and current_row > 0:
			current_row -= 1
			updateMenu(current_row, menu)
		elif key == curses.KEY_DOWN and current_row < len(menu['options'])-1:
			current_row += 1
			updateMenu(current_row, menu)
		elif key == curses.KEY_ENTER or key in [10, 13]:
			# if type is 'command'
			if menu['options'][current_row]['type'] == 'command':
				if menu['options'][current_row]['command'] == 'BACK':
					# view parent menu
					# pfusch ...
					time_parent = int(round(time.time() * 1000)) # in ms 
					updateMenu(current_row, parent.pop(-1))
				else:
					# return command value
					return menu['options'][current_row]['command'] # return command
			# if type is 'menu'
			if menu['options'][current_row]['type'] == 'menu':
				# access submenu
				# ... pfusch
				if int(round(time.time() * 1000)) - time_parent > 10:
					updateMenu(current_row, menu['options'][current_row], menu) # display the submenu
					current_row = 0


def on_subscribe(client, userdata, mid, granted_qos):
	logging.info('GUITask\t\tSubscribed to SensorTask')
def on_unsubscribe(client, userdata, mid):
	pass

def on_message(client, userdata, msg):
	def topic(message):
		global last_stamp, drift, format_param, drift_flag 
		stamp = float(message['timestamp'])
		value = float(message['temperature'])
		dt = stamp - last_stamp
		jitter = dt - 0.1
		if drift_flag == True:
			drift += jitter
		else:
			drift_flag = True
		last_stamp = stamp

		print("temperature: " + str(value) \
			+ "\tstamp: " + format_param.format(stamp) \
			+ "\tjitter: " + format_param.format(jitter) \
			+ "\tdrift: " + format_param.format(drift)) 


	dict = json.loads(msg.payload.decode('utf-8'))    
	if disp == 1:
		print(dict)
	if disp == 2:
		topic(dict)



def display_topic(topic):
	global client, disp, drift_flag
	client.subscribe(topic, qos=0)
	client.loop_start()
	disp = 1
	input()
	disp = 0
	client.loop_stop()

def display_data(topic):
	global client, disp, drift_flag
	client.subscribe(topic, qos=0)
	client.loop_start()
	disp = 2
	input()
	disp = 0
	client.loop_stop()
	drift_flag = False



if __name__ == '__main__':
	#load menu params
	param_file = open("gui_params.json")
	menu_data = json.load(param_file)
	#init logging module
	logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
	logging.info('GUITask\t\tstart')
	#define os priority
	niceValue = os.nice(10)
	logging.info('GUITask\t\tniceValue:%s',niceValue)

	client = paho.Client()
	client.on_message = on_message
	client.on_subscribe = on_subscribe
	client.on_unsubscribe = on_unsubscribe
	client.connect(host='localhost',port= 1883)


	while True:
		#start GUI blocking
		reply = curses.wrapper(GUI)
		if(reply == 'Exit'):
			sys.exit(0)
		if(reply == 'topic_temprature'):
			display_topic('SensorTask/Temperature')
		if(reply == 'data_temperature'):
			display_data('SensorTask/Temperature')









