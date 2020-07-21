import paho.mqtt.client as paho
import os
import time
import json
import curses
import sys
import logging
import constants

menu = None
parent = []
login_status = False

disp = 0
msg_name = None
msg_type = None
value3_type = None

last_stamp = 0
drift = 0
drift_flag = False
format_param = constants.timestamp_format
value_param = constants.value_format


def GUI(stdscr):
	time_parent = 0
	global menu, menu_data

	if not menu:
		menu = menu_data

	def updateMenu(current_row, menu_var, parent_var=None):
		global menu
		if menu != menu_var:
			# set cursor to 0 if new menu is opend
			menu = menu_var
			current_row = 0
		if parent_var:
			# append parent menu to list (fifo)
			global parent
			parent.append(parent_var)
		# check user status
		user_s = set_user()
		# start gui printing
		stdscr.clear()
		try:
			stdscr.addstr(1, 2, menu['title'], curses.A_UNDERLINE)  # Title for this menu
			stdscr.addstr(2, 2,"user: " + user_s) # print user 
			stdscr.addstr(4, 2, menu['subtitle'], curses.A_BOLD)  # Subtitle for this menu
		except:
			# pass known curses bug, resticts no functionality
			pass
		for idx in range(len(menu_var['options'])):
			if idx == current_row:
				# print line with cursor
				stdscr.attron(curses.color_pair(1))
				try:
					stdscr.addstr(idx + 5, 4, '%s - %s' % ('{:3}'.format(idx + 1), menu_var['options'][idx]['title']))
				except:
					# pass known curses bug, resticts no functionality
					pass
				stdscr.attroff(curses.color_pair(1))
			else:
				# print other lines
				try:
					stdscr.addstr(idx + 5, 4, '%s - %s' % ('{:3}'.format(idx + 1), menu_var['options'][idx]['title']))
				except:
					# pass known curses bug, resticts no functionality
					pass

	def set_user():
		global login_status
		# load user file
		try:	
			user_file = open("user.txt")
		except:
			logging.info('GUITask\t\tabort: no user.txt')
			print("abort: no user.txt")
			sys.exit(1)
		user_s = user_file.read()
		if user_s != '':
			user_data = json.loads(user_s)
			try:
				if user_data["login"] == "True":
					# set login_status and return user name
					login_status = True
					return user_data['user']['userName']
			except:
				pass
		# set login_status and return user name
		login_status = False
		return "-"


	stdscr.clear()
	#stdscr.timeout(100)
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
				elif menu['options'][current_row]['command'] == 'Exit':
					# end program
					sys.exit(0)
				else:
					# return command value and command type
					return (menu['options'][current_row]['command'], menu['cmd_type'])
			# if type is 'menu'
			if menu['options'][current_row]['type'] == 'menu':
				# access submenu
				if int(round(time.time() * 1000)) - time_parent > 10: # bugfix
					updateMenu(current_row, menu['options'][current_row], menu)  # display the submenu
					current_row = 0


def on_subscribe(client, userdata, mid, granted_qos):
	logging.info('GUITask\t\tSubscribed to SensorTask')


def on_unsubscribe(client, userdata, mid):
	pass


def on_message(client, userdata, msg):
	def topic(message):
		global  msg_type, msg_name, disp, value3_type, \
			format_param, value_param, drift_flag
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
		(stamp, dt, jitter, drift) = processTimestamp(float(msg['timestamp']))
		
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
			+ "dt: " + format_param.format(dt) + "  |  " \
			+ "jitter: " + format_param.format(jitter) + "  |  " \
			+ "drift: " + format_param.format(drift))

	def processTimestamp(stamp):
		global last_stamp, drift, drift_flag, login_status
		# compute dt, jitter and drift
		if drift_flag:
			dt = stamp - last_stamp
			if login_status:
				jitter = dt - constants.measurementPeriodLogin
			else:
				jitter = dt - constants.measurementPeriodLogout
			drift += jitter
		else:
			dt = 0
			jitter = 0
			drift_flag = True
		last_stamp = stamp
		return(stamp, dt, jitter, drift)


	# load payload
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
	client.subscribe(constants.local_sensor_topic, qos=0)
	client.loop_start()
	disp = 2
	input()
	disp = 0
	client.loop_stop()
	client.unsubscribe(constants.local_sensor_topic)
	drift_flag = False
	drift = 0


if __name__ == '__main__':
	# init logging module
	logging.basicConfig(filename='logFile.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
	logging.info('GUITask\t\tstart')
	# load menu params
	try:
		param_file = open("gui_params.json")
	except:
		logging.info('GUITask\t\tabort: no gui_params.json')
		print("abort: no gui_params.json")
		sys.exit(1)
	menu_data = json.load(param_file)
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
		(cmd, cmd_type) = curses.wrapper(GUI)
		cmd_tuple = cmd.split()
		# topics
		if cmd_type == 'Topics':
			display_topic(cmd_tuple[0])
		# sensorValue1
		elif cmd_type == 'SensorValue1':
			msg_name = cmd_tuple[0]
			msg_type = 1
			display_data()
		# sensorValue3
		elif cmd_type == 'SensorValue3':
			msg_name = cmd_tuple[0]
			msg_type = 3
			value3_type = cmd_tuple[1]
			display_data()

