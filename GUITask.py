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

def GUI(stdscr):
    time_parent = 0
    MENU = "menu"
    COMMAND = "command"
    VALUE = "value"

    menu_data = {
    'title': "Vehicle 3 GUI", 'type': MENU, 'subtitle': "Please selection an option...",
    'options': [
        {
        'title': "View Sensor Data", 'type': MENU, 'subtitle':"Sensor Data",
        'options': [
            { 'title': "Back", 'type': COMMAND, 'command': 'BACK' },
            { 'title': "Temperature", 'type': VALUE, 'unit': '°C' },
            { 'title': "Exit", 'type': COMMAND, 'command':"Exit"  }, 
        ] 
        },   
        {
        'title': "View Topics", 'type': MENU, 'subtitle':"Sensor Data",
        'options': [
            { 'title': "Back", 'type': COMMAND, 'command': 'BACK' },
            { 'title': "View Temperature Topic", 'type': COMMAND, 'command': 'View Temperature Topic' },
            { 'title': "View Temperature Topic", 'type': COMMAND, 'command': 'View Temperature Topic' },
            { 'title': "View Temperature Topic", 'type': COMMAND, 'command': 'View Temperature Topic' },
            { 'title': "View Temperature Topic", 'type': COMMAND, 'command': 'View Temperature Topic' },
            { 'title': "Exit", 'type': COMMAND, 'command':"Exit"  }, 
        ] 
        },
        {    
        'title': "Scoreboard", 'type': MENU, 'subtitle':"Sensor Data",
        'options': [
            { 'title': "Back", 'type': COMMAND, 'command': 'BACK' },
            { 'title': "Exit", 'type': COMMAND, 'command':"Exit"  }, 
        ] 
        },
        {    
        'title': "Exit", 'type': COMMAND, 'command':"Exit"
        },   
    ]
    }
    global menu
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
                stdscr.attron(curses.color_pair(1))
                stdscr.addstr(idx+4,4,"%d - %s" % (idx+1, menu_var['options'][idx]['title']))
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(idx+4,4,"%d - %s" % (idx+1, menu_var['options'][idx]['title']))

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
            if menu['options'][current_row]['type'] == COMMAND:
                if menu['options'][current_row]['command'] == 'BACK':
                    # view parent menu
                    # pfusch ...
                    time_parent = int(round(time.time() * 1000)) # in ms 
                    updateMenu(current_row, parent.pop(-1))
                else:
                    # return command value
                    return menu['options'][current_row]['command'] # return command
            # if type is 'menu'
            if menu['options'][current_row]['type'] == MENU:
                # access submenu
                # ... pfusch
                if int(round(time.time() * 1000)) - time_parent > 10:
                    updateMenu(current_row, menu['options'][current_row], menu) # display the submenu
                    current_row = 0



#init logging module
logging.basicConfig(filename='logFile.log',format='%(asctime)s %(message)s',level=logging.DEBUG)
logging.info('GUITask\t\tstart')

niceValue = os.nice(10)
logging.info('GUITask\t\tniceValue:%s',niceValue)


def on_subscribe(client, userdata, mid, granted_qos):
	logging.info('GUITask\t\tSubscribed to SensorTask')
def on_message(client, userdata, msg):
	dict = json.loads(msg.payload.decode('utf-8'))
	if disp: print(dict)


disp = False

while True:
	#start GUI blocking
	reply = curses.wrapper(GUI)
	if(reply == 'Exit'):
		sys.exit(0)
	if(reply == 'View Temperature Topic'):
		client = paho.Client()
		client.on_message = on_message
		client.on_subscribe = on_subscribe
		client.connect(host='localhost',port= 1883)
		client.subscribe('SensorTask/Temperature', qos=0)
		client.loop_start()
		disp = True
		input()
		disp = False
		client.loop_stop()







