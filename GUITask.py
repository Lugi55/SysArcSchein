import paho.mqtt.client as paho
import os
import time
import json
import curses
import sys
import logging

menu = None
parent = []
user_s = "-"

disp = 0
msg_name = None
msg_type = None
value3_type = None

last_stamp = 0
drift = 0
drift_flag = False
format_param = '{:016.6f}'
value_param = '{:10.4f}'


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
		try:
			stdscr.addstr(1, 2, menu['title'], curses.A_UNDERLINE)  # Title for this menu
			stdscr.addstr(2, 2,"user: " + user_s) # print user 
			stdscr.addstr(4, 2, menu['subtitle'], curses.A_BOLD)  # Subtitle for this menu
		except:
			pass
		for idx in range(len(menu_var['options'])):
			if idx == current_row:
				# print line with cursor
				stdscr.attron(curses.color_pair(1))
				try:
					stdscr.addstr(idx + 5, 4, '%s - %s' % ('{:3}'.format(idx + 1), menu_var['options'][idx]['title']))
				except:
					pass
				stdscr.attroff(curses.color_pair(1))
			else:
				# print other lines
				try:
					stdscr.addstr(idx + 5, 4, '%s - %s' % ('{:3}'.format(idx + 1), menu_var['options'][idx]['title']))
				except:
					pass

	stdscr.clear()
	curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
	curses.curs_set(0)
	current_row = 0
	updateMenu(current_row, menu)

	while 1:
		key = stdscr.getch()
		if key == curses.KEY_UP and current_row > 0:
			current_row -= 1
			updateMenu(current_row, menu)
		elif key == curses.KEY_DOWN and current_row < len(menu['options']) - 1:
			current_row += 1
			updateMenu(current_row, menu)
		elif key == curses.KEY_ENTER or key in [10, 13]:
			# if type is 'command'
			if menu['options'][current_row]['type'] == 'command':
				if menu['options'][current_row]['command'] == 'BACK':
					# view parent menu
					time_parent = int(round(time.time() * 1000))  # in ms
					updateMenu(current_row, parent.pop(-1))
				else:
					# return command value
					return menu['options'][current_row]['command']  # return command
			# if type is 'menu'
			if menu['options'][current_row]['type'] == 'menu':
				# access submenu
				if int(round(time.time() * 1000)) - time_parent > 10:
					updateMenu(current_row, menu['options'][current_row], menu)  # display the submenu
					current_row = 0


def on_subscribe(client, userdata, mid, granted_qos):
	logging.info('GUITask\t\tSubscribed to SensorTask')


def on_unsubscribe(client, userdata, mid):
	pass


def on_message(client, userdata, msg):
	def topic(message):
		global last_stamp, msg_type, msg_name, disp, value3_type
		global drift, format_param, value_param, drift_flag
		try:
			length = len(message['SensorValue' + str(msg_type)])
			msg = None
			for i in range(length):
				# somehow a bug with "if is" statement 
				if message['SensorValue' + str(msg_type)][i]['name'] == msg_name:
					msg = message['SensorValue' + str(msg_type)][i]
					break
			if not msg:
				print("Requested data not in message!\nPlease press ENTER.")
				disp = 0
				return	
		except:
			print("Requested data not in message!\nPlease press ENTER.")
			disp = 0
			return
		# process timestamp
		stamp = float(msg['timestamp'])
		dt = stamp - last_stamp
		if drift_flag:
			jitter = dt - 0.1
			drift += jitter
		else:
			jitter = 0
			drift_flag = True
		last_stamp = stamp
		# process value
		if msg_type is 1:
			value = value_param.format(float(msg['value']))

		elif msg_type is 3:
			valueX = value_param.format(float(msg['valueX']))
			valueY = value_param.format(float(msg['valueY']))
			valueZ = value_param.format(float(msg['valueZ']))

			if value3_type is "x":
				value = valueX
			elif value3_type is "y":
				value = valueY
			elif value3_type is "z":
				value = valueZ
			else:
				value = "X: " + valueX + "   Y: " + valueY + "   Z: " + valueZ
		# print data (/t not useful)
		print(msg_name + ": " + str(value) + "  |  " \
			  + "stamp: " + format_param.format(stamp) + "  |  " \
			  + "jitter: " + format_param.format(jitter) + "  |  " \
			  + "drift: " + format_param.format(drift))

	dict = json.loads(msg.payload.decode('utf-8'))
	if disp == 1:
		print(str(dict) + "\n")
	if disp == 2:
		topic(dict)


def display_topic(topic):
	global client, disp, drift_flag
	# clear terminal
	os.system('clear')
	client.subscribe(topic, qos=0)
	client.loop_start()
	disp = 1
	input()
	disp = 0
	client.loop_stop()
	client.unsubscribe(topic)


def display_data():
	global client, disp, drift_flag, drift
	# clear terminal
	os.system('clear')
	client.subscribe('local/sensor', qos=0)
	client.loop_start()
	disp = 2
	input()
	disp = 0
	client.loop_stop()
	client.unsubscribe('local/sensor')
	drift_flag = False
	drift = 0


if __name__ == '__main__':
	# load menu params
	param_file = open("gui_params.json")
	menu_data = json.load(param_file)
	# init logging module
	logging.basicConfig(filename='logFile.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
	logging.info('GUITask\t\tstart')
	# define os priority
	niceValue = os.nice(10)
	logging.info('GUITask\t\tniceValue:%s', niceValue)

	client = paho.Client()
	client.on_message = on_message
	client.on_subscribe = on_subscribe
	client.on_unsubscribe = on_unsubscribe
	client.connect(host='localhost', port=1883)

	while True:
		# start GUI blocking
		rc = curses.wrapper(GUI)
		rc_list = rc.split()
		# exit
		if rc_list[0] == 'Exit':
			sys.exit(0)
		# topics
		elif rc_list[0] == 'local/#':
			display_topic(rc_list[0])
		elif rc_list[0] == 'local/sensor':
			display_topic(rc_list[0])
		elif rc_list[0] == 'local/com2/#':
			display_topic(rc_list[0])
		elif rc_list[0] == 'local/com2/car':
			display_topic(rc_list[0])
		elif rc_list[0] == 'local/com2/web':
			display_topic(rc_list[0])
		# sensorValue1
		elif rc_list[0] == 'LIDAR':
			msg_name = rc_list[0]
			msg_type = 1
			display_data()
		elif rc_list[0] == 'Humidity':
			msg_name = rc_list[0]
			msg_type = 1
			display_data()
		elif rc_list[0] == 'SteeringAngle':
			msg_name = rc_list[0]
			msg_type = 1
			display_data()
		elif rc_list[0] == 'Temperature':
			msg_name = rc_list[0]
			msg_type = 1
			display_data()
		elif rc_list[0] == 'Speed':
			msg_name = rc_list[0]
			msg_type = 1
			display_data()
		elif rc_list[0] == 'Altimeter':
			msg_name = rc_list[0]
			msg_type = 1
			display_data()
		elif rc_list[0] == 'Acceleration':
			msg_name = rc_list[0]
			msg_type = 3
			value3_type = rc_list[1]
			display_data()
		elif rc_list[0] == 'Magnetometer':
			msg_name = rc_list[0]
			msg_type = 3
			value3_type = rc_list[1]
			display_data()
		elif rc_list[0] == 'Gyro':
			msg_name = rc_list[0]
			msg_type = 3
			value3_type = rc_list[1]
			display_data()
		# delete list items
		del rc_list
