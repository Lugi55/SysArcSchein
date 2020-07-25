import paho.mqtt.client as paho
import os
import time
import json
import curses
import sys
import logging
import threading
import constants

format_param = constants.timestamp_format
value_param = constants.value_format



class GUIMenu:
	__user_s = "-"

	__menu = None
	__menu_data = None
	__parent = []

	def __init__(self):
		# load self.__menu params
		try:
			param_file = open("gui_params.json")
		except:
			logging.info('GUITask\t\t\tabort: no gui_params.json')
			print("abort: no gui_params.json")
			sys.exit(1)
		self.__menu_data = json.load(param_file)


	def set_user_s(self, user_s):
		self.__user_s = user_s


	def __updateMenu(self, stdscr, current_row, menu_var, parent_var=None):
		if self.__menu != menu_var:
			# set cursor to 0 if new menu is opened
			self.__menu = menu_var
			current_row = 0
		if parent_var:
			# append parent menu to list (fifo)
			self.__parent.append(parent_var)
		# start gui printing
		stdscr.clear()
		try:
			stdscr.addstr(1, 2, self.__menu['title'], curses.A_UNDERLINE)  # Title for this menu
			stdscr.addstr(2, 2,"user: " + self.__user_s) # print user 
			stdscr.addstr(4, 2, self.__menu['subtitle'], curses.A_BOLD)  # Subtitle for this menu
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


	def drawGUI(self, stdscr):
		time_parent = 0
		
		if not self.__menu:
			self.__menu = self.__menu_data

		stdscr.clear()
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
		curses.curs_set(0)
		current_row = 0
		self.__updateMenu(stdscr, current_row, self.__menu)

		while 1:
			# blocking
			key = stdscr.getch()
			if key == curses.KEY_UP and current_row > 0:
				current_row -= 1
				self.__updateMenu(stdscr, current_row, self.__menu)
			elif key == curses.KEY_DOWN and current_row < len(self.__menu['options']) - 1:
				current_row += 1
				self.__updateMenu(stdscr, current_row, self.__menu)
			elif key == curses.KEY_ENTER or key in [10, 13]:
				# if type is 'command'
				if self.__menu['options'][current_row]['type'] == 'command':
					if self.__menu['options'][current_row]['command'] == 'BACK':
						# view parent menu
						time_parent = int(round(time.time() * 1000))  # in ms
						self.__updateMenu(stdscr, current_row, self.__parent.pop(-1))
					elif self.__menu['options'][current_row]['command'] == 'Exit':
						# end program
						return ('', 'Exit')
					else:
						# return command value and command type
						return (self.__menu['options'][current_row]['command'], self.__menu['cmd_type'])
				# if type is 'self.__menu'
				if self.__menu['options'][current_row]['type'] == 'menu':
					# access submenu
					if int(round(time.time() * 1000)) - time_parent > 10: # bugfix
						self.__updateMenu(stdscr, current_row, self.__menu['options'][current_row], self.__menu)  # display the submenu
						current_row = 0



class GUImessages:
	__login_status = False

	__last_stamp = None
	__disp = None
	__drift_flag = None
	__drift = None
	__msg_name = None
	__value3_type = None

	def __init__(self):
		# init MQTT client
		self._client = paho.Client()
		self._client.on_message = self._on_message
		self._client.on_subscribe = self._on_subscribe
		self._client.on_unsubscribe = self._on_unsubscribe
		self._client.connect(host='localhost', port=1883)


	def set_login_status(self, login_status):
		self.__login_status = login_status


	def display_topic(self, topic):
		# clear terminal
		os.system('clear')
		print("Press ENTER to return to menu!\n")
		self._client.subscribe(topic, qos=0)
		self._client.loop_start()
		input()
		self._client.loop_stop()
		self._client.unsubscribe(topic)


	def display_data(self, msg_name, value3_type=None):
		self.__msg_name = msg_name
		self.__value3_type = value3_type
		# clear terminal
		os.system('clear')
		print("Press ENTER to return to menu!\n")
		self._client.subscribe(constants.local_sensor_topic, qos=0)
		self._client.loop_start()
		input()
		self._client.loop_stop()
		self._client.unsubscribe(constants.local_sensor_topic)
		self.__msg_name = None
		self.__drift_flag = False
		self.__drift = 0


	def _on_subscribe(self, client, userdata, mid, granted_qos):
		logging.info('GUITask\t\t\tSubscribed to SensorTask')

	def _on_unsubscribe(self, client, userdata, mid):
		pass

	def _on_message(self, client, userdata, msg):
		# load payload
		dict = json.loads(msg.payload.decode('utf-8'))
		if not self.__msg_name:
			print(str(dict) + "\n")
		elif self.__msg_name == "Stop":
			pass
		else:
			self.__print_topic(dict)

	
	def __print_topic(self, message):
		if not self.__value3_type:
			msg_type = 1
		else:
			msg_type = 3 
		try:
			length = len(message['SensorValue' + str(msg_type)])
			msg = None
			for i in range(length):
				# somehow a bug with "if is" statement 
				if message['SensorValue' + str(msg_type)][i]['name'] == self.__msg_name:
					msg = message['SensorValue' + str(msg_type)][i]
					break
			if not msg:
				print("Requested data not in message!\nPlease press ENTER.")
				self.__msg_name = "Stop"
				return	
		except:
			print("Requested data not in message!\nPlease press ENTER.")
			self.__msg_name = "Stop"
			return
		# process timestamp
		(stamp, dt, jitter, drift) = self.__processTimestamp(float(msg['timestamp']))
		
		# process value
		format_param = constants.timestamp_format
		value_param = constants.value_format

		if not self.__value3_type:
			value = value_param.format(float(msg['value']))

		else:
			valueX = value_param.format(float(msg['valueX']))
			valueY = value_param.format(float(msg['valueY']))
			valueZ = value_param.format(float(msg['valueZ']))

			if self.__value3_type is "x":
				value = valueX
			elif self.__value3_type is "y":
				value = valueY
			elif self.__value3_type is "z":
				value = valueZ
			else:
				value = "X: " + valueX + "   Y: " + valueY + "   Z: " + valueZ
		# print data (/t not useful)
		print(self.__msg_name + ": " + value + "  |  " \
			+ "stamp: " + format_param.format(stamp) + "  |  " \
			+ "dt: " + format_param.format(dt) + "  |  " \
			+ "jitter: " + format_param.format(jitter) + "  |  " \
			+ "drift: " + format_param.format(drift))


	def __processTimestamp(self,stamp):
		# compute dt, jitter and drift
		if self.__drift_flag:
			dt = stamp - self.__last_stamp
			if self.__login_status:
				jitter = dt - constants.measurementPeriodLogin
			else:
				jitter = dt - constants.measurementPeriodLogout
			self.__drift += jitter
		else:
			dt = 0
			jitter = 0
			self.__drift = 0
			self.__drift_flag = True
		self.__last_stamp = stamp
		return(stamp, dt, jitter, self.__drift)


class GUITask:
	__Finish = False

	def __init__(self):
		logging.info('GUITask\t\t\tstart')
		self.__gui_menu = GUIMenu()
		self.__gui_messages = GUImessages()

	def set_user_s(self, user_s):
		with lock:
			self.__gui_menu.set_user_s(user_s)

	def set_login_status(self, login_status):
		with lock:
			self.__gui_messages.set_login_status(login_status)

	def get_finish(self):
		with lock:
			return self.__Finish
	
	def set_finish(self, finish ):
		with lock:
			self.__Finish = finish

	def guiTask(self):
		# wait for LoginStatusTask
		time.sleep(0.2)
		# loop forever
		while True:
			# start GUI blocking
			(cmd, cmd_type) = curses.wrapper(self.__gui_menu.drawGUI)
			cmd_tuple = cmd.split()
			# topics
			if cmd_type == 'Topics':
				self.__gui_messages.display_topic(cmd_tuple[0])
			# sensorValue1
			elif cmd_type == 'SensorValue1':
				self.__gui_messages.display_data(cmd_tuple[0])
			# sensorValue3
			elif cmd_type == 'SensorValue3':
				self.__gui_messages.display_data(cmd_tuple[0], cmd_tuple[1])
			# exit
			elif cmd_type == 'Exit':
				self.__Finish = True
				break



class LoginStatusTask():
	__gui = None


	def __init__(self, gui):
		self.__gui = gui
		logging.info('GUITask\t\t\tloginStatusTask started')

	def check_login_status(self):
		# loop forever
		while True:
			if self.__gui.get_finish():
				break
			(user_s, login_status) = self.__check_file()
			# set login status
			gui.set_login_status(login_status)
			# get user string
			gui.set_user_s(user_s)
			# sleep
			time.sleep(constants.loginStatusPeriod)

	def __check_file(self):
		# load user file
		try:	
			user_file = open("user.txt")
		except:
			logging.info('GUITask\t\t\tabort: no user.txt')
			print("abort: no user.txt")
			gui.set_finish(True)
		user_s = user_file.read()
		if user_s != '':
			user_data = json.loads(user_s)
			try:
				if user_data["login"] == True:
					# set login_status and return user name
					return (user_data['user']['userName'], True)
			except:
				pass
		# set login_status and return user name
		return ("-", False)




if __name__ == '__main__':
	# init logging module
	logging.basicConfig(filename='logFile.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
	# define os priority
	niceValue = os.nice(constants.GUITaskNiceness)
	logging.info('GUITask\t\t\tniceValue:%s', niceValue)
	# GUITask obj
	gui = GUITask()
	# LoginStatusTask obj
	status = LoginStatusTask(gui)
	# use threads
	lock = threading.Lock()
	t1 = threading.Thread(target=status.check_login_status)
	t2 = threading.Thread(target=gui.guiTask)

	t1.start()
	t2.start()

	t1.join()
	t2.join()
	logging.info('GUITask\t\t\tstopped')

