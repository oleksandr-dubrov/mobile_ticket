#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '1.0'
__author__ = 'Olexandr Dubrov <olexandr.dubrov@gmail.com>'
__license__ = '''
	Mobile ticket is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	Bluetube is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with Bluetube.  If not, see <https://www.gnu.org/licenses/>.
'''

import os
import sys
import re
from datetime import datetime

SYMBIAN = sys.platform == 'symbian_s60'

if SYMBIAN:
	import e32  # @UnresolvedImport @UnusedImport
	import appuifw  # @UnresolvedImport @UnusedImport
	import messaging	# @UnresolvedImport @UnusedImport
	import inbox	# @UnresolvedImport @UnusedImport
else:
	import symbian.appuifw as appuifw  # @Reimport
	import symbian.e32 as e32  # @Reimport
	import symbian.inbox as inbox  # @Reimport
	import symbian.messaging as messaging  # @Reimport

PHONE_NUMBER = '877'


# ####################################
# ###################################
# def sms_send(number, msg, callback=None, name=None):
# 	callback(messaging.ESent)
# 
# messaging.sms_send = sms_send
# ###################################
# ####################################

class Ticket:
	'''Manages a saved ticket'''

	if SYMBIAN:
		TICKETS_PATH = 'e:\\data\\python\\resources\\mobile_ticket\\ticket.txt'
	else:
		TICKETS_PATH = os.path.normpath('data/ticket.txt')
	EXPIRE_PATTERN = u'Дійсний до: (?P<hours>\d{1,2}):(?P<minutes>\d{2}) (?P<day>\d{1,2}).(?P<month>\d{2}).(?P<year>\d{4})'

	def __init__(self):
		self._pattern = re.compile(Ticket.EXPIRE_PATTERN, re.UNICODE)
		self._ticket = ''
		if not (os.path.exists(Ticket.TICKETS_PATH) and os.path.isfile(Ticket.TICKETS_PATH)):
			self.save()

	def _get_rid_of_expired_tickets(self):
		print self._ticket
		m = self._pattern.match(self._ticket)
		assert m, 'malformed ticket'
		exire_time = datetime(int(m.group('year')),
							int(m.group('month')),
							int(m.group('day')),
							hour=int(m.group('hours')),
							minute=int(m.group('minutes')))
		print exire_time
		print datetime.now()
		if exire_time < datetime.now():
			self._ticket = ''

	def get_content(self):
		if self._ticket == '' and os.path.getsize(Ticket.TICKETS_PATH):
			f = open(Ticket.TICKETS_PATH, 'r')
			self._ticket = unicode(f.read())
			f.close()
		
		if self._ticket:
			self._get_rid_of_expired_tickets()

		return self._ticket
	
	def set(self, ticket):
		self._ticket = ticket

	def save(self):
		f = open(Ticket.TICKETS_PATH, 'w')
		f.write(self._ticket.encode('utf-8'))
		f.close()


class DB:
	'''Manages the db'''

	if SYMBIAN:
		DB_PATH = 'e:\\data\\python\\resources\\mobile_ticket\\mobtick.bd'
	else:
		DB_PATH = os.path.normcase('data/mobtick.bd')

	def __init__(self):
		self._last_err_msg = ''
		self._data = []

	def _check_db_file(self):
		return os.path.exists(DB.DB_PATH) and os.path.isfile(DB.DB_PATH)

	def get_last_err_msg(self):
		return self._last_err_msg

	def get_help(self):
		return u'''The DB is a file in the %s directory. Each line in the file must be like this:
transport type,transport code,rote 1,route 2,...,route N
Example:
tram,SAC,1,2,3,4,5,6
The db file should be shipped with the application.
'''%(os.path.dirname(DB.DB_PATH))

	def connect(self):
		if not self._check_db_file():
			self._last_err_msg = u'The DB file %s is not found. See console output for more info.'%DB.DB_PATH
			return False
		f = open(DB.DB_PATH, 'r');
		for line in f.readlines():
			if line.startswith('#'):
				continue
			lst = line.strip().split(',')
			self._data.append({'type': unicode(lst[0]),
								'code': unicode(lst[1]),
								'routes': [unicode(x) for x in lst[2:]]})
		f.close()
		return True

	def disconnect(self):
		pass

	def get_transport_types(self):
		return [e['type'] for e in self._data]

	def get_routes(self, transport_type):
		return [e for e in self._data if e['type'] == transport_type][0]['routes']
						
	def get_code(self, transport_type):
		return [e for e in self._data if e['type'] == transport_type][0]['code']

class Listbox():
	'''Extends appuifw Listbox'''

	def __init__(self, init_list, cb_handler):
		self._lst = init_list
		self._ui_list = appuifw.Listbox(self._lst, cb_handler)
		self._ui_list.bind(0x35, cb_handler) # bind the handler to key 5
		self._ui_list.bind(0x32, self.cb_focus_up) # bind the handler to key 2
		self._ui_list.bind(0x38, self.cb_focus_down) # bind the handler to key 8

	def current_item(self):
		idx = self._ui_list.current()
		return self._lst[idx]

	def set_list(self, lst):
		self._lst = lst
		self._ui_list.set_list(self._lst, self._ui_list.current())

	def cb_focus_up(self):
		pos = self._ui_list.current() - 1
		if pos < 0:
			pos = len(self._lst) - 1
		self._ui_list.set_list(self._lst, pos)

	def cb_focus_down(self):
		pos = self._ui_list.current() + 1
		if pos > len(self._lst) - 1:
			pos = 0
		self._ui_list.set_list(self._lst, pos)

	def get_body(self):
		return self._ui_list


class SMS:
	'''Works with the SMS service'''
	SUCCESS_REQUEST = ['Дякуємо за заявку.', 'Oчікуйте SMS']
	ETICKET_HEADER = ['Оплата проїзду успішна!']
	
	def __init__(self, cb_info_received, cb_ticket_recieved):
		self._cb_info_received = cb_info_received
		self._cb_ticket_recieved = cb_ticket_recieved

	def _message_received(self, msg_id):
		box = inbox.Inbox()
		sender = box.address(msg_id)
		if sender == PHONE_NUMBER:
			msg = box.content(msg_id)
			if SMS.SUCCESS_REQUEST[0] in msg and SMS.SUCCESS_REQUEST[1] in msg:
				box.delete(msg_id)
				self._cb_info_received(msg)
			if SMS.ETICKET_HEADER in msg:
				self._cb_ticket_recieved(msg)
			self._cb_info_received(msg)

	@staticmethod
	def compose_txt(code, route):
		return '%s%s'%(code, route)

	def send(self, msg):
		sent = False

		def _cb_sent(state):
			if state == messaging.ESent:
				sent = True
			if state in [messaging.EScheduleFailed, messaging.ESendFailed, messaging.EFatalServerError]:
				sent = False

		#messaging.sms_send(PHONE_NUMBER, msg, callback=_cb_sent, name="e-ticket")

		#### box = inbox.Inbox()
		#### box.bind(self._message_received)

		################################
		
		self._cb_ticket_recieved(u'''Оплата проїзду успішна!
Код перевірки: № 31284122
Маршрут: №6a
Транспорт: Тролейбус
Місто: Вінниця
Сума: 4 грн
Дійсний до: 00:38 17.11.2019
-------------------------------
Швидкі перекази та платежі на сайті: kv.st/sm-catalog''')
		################################

		return sent


class MobileTicket:
	'''Mobile ticket.'''

	def __init__(self):
		appuifw.app.screen = "normal"
		appuifw.app.exit_key_handler = self.quit

		self._db = DB()
		if not self._db.connect():
			appuifw.note(self._db.get_last_err_msg(), 'error')
			assert 0, self._db.get_help()
		self._ticket = Ticket()
		self._body = None

	def _set_list_body(self):
		lst = Listbox(self._db.get_transport_types(), self.at_list_handler)
		appuifw.app.title = u'Мобільний квиток'
		appuifw.app.body = lst.get_body()
		appuifw.app.menu = [
					(u'Select', self.at_list_handler),
					(u'Show the ticket', self.at_show_ticket),
					(u'Help', self.at_help),
					(u'Info', self.about),
				]
		self._body = lst

	def _set_text_body(self):
		txt = appuifw.Text()
		txt.font = "annotation"
		appuifw.app.title = u'Дійсний квиток'
		appuifw.app.body = txt
		appuifw.app.menu = [
					(u'Back', self.at_back),
				]
		self._body = txt

	def _send_request(self, code, route):
		sms = SMS(self._cb_info_received, self._cb_ticket_recieved)
		txt = SMS.compose_txt(code, route)
		i = appuifw.InfoPopup()
		i.show(u'Please wait for a while.', (0, 0), 60000, 0, appuifw.EHRightVCenter)
		success = sms.send(txt)
		i.hide()
# 		if success:
# 			i.show(u'Wait a minute or so for a ticket', (0, 0), 5*60000, 0, appuifw.EHRightVCenter)
# 			self._set_text_body()
# 		else:
# 			appuifw.note(u'Failed to send request. Try again later.', 'error')

	def _cb_info_received(self, msg):
		self._set_text_body()
		self._body.set(msg)
	
	def _cb_ticket_recieved(self, ticket):
		appuifw.note(u'Your e-ticket has arrived!', 'conf')
		self._set_text_body()
		self._body.set(ticket)
		self._body.set_pos(39)
		self._ticket.set(ticket)

	def run(self):
		self._set_list_body()
		self._script_lock = e32.Ao_lock()
		self._script_lock.wait()

	def at_list_handler(self):
		trans_type = self._body.current_item()
		routes = self._db.get_routes(trans_type)
		idx = appuifw.selection_list(routes, search_field=1)
		if not idx == None:
			self._send_request(self._db.get_code(trans_type), routes[idx])

	def at_show_ticket(self):
		ticket = self._ticket.get_content()
		if ticket:
			self._set_text_body()
			self._body.set(ticket)
			self._ticket.set(ticket)
		else:
			appuifw.note(u'No ticket', 'error')

	def at_back(self):
		self._set_list_body()

	def at_help(self):
		appuifw.note(u'1. Select a transport.\n2. Select a route.\n3. Wait for a ticket.', 'info')

	def about(self):
		appuifw.note(u'Mobile ticket v.%s' % __version__, 'info')

	def quit(self):
		self._db.disconnect()
		self._ticket.save()
		appuifw.app.exit_key_handler = None
		self._script_lock.signal()


if __name__ == '__main__':
	MobileTicket().run()
