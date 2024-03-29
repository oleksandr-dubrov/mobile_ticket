#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '1.1'
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

import appuifw  # @UnresolvedImport @UnusedImport
import e32  # @UnresolvedImport @UnusedImport
import messaging  # @UnresolvedImport @UnusedImport

PHONE_NUMBER = '877'


class Localizer:
    '''Localize the string'''

    UA = 'ua'
    ENG = 'eng'
    MOBILE_TICKET = u'Mobile ticket'
    WAIT_FOR_A_TICKET = u'Wait for a ticket from %s.' % PHONE_NUMBER

    def __init__(self, lang=ENG):
        self._lang = lang
        self._ua_strings = {
            Localizer.MOBILE_TICKET: u'Мобільний квиток',
            u'Select': u'Вибрати',
            u'Get a duplicate': u'Отримати дублікат',
            u'Help': u'Допомога',
            u'Info': u'Інформація',
            u'Please wait, sending is ongoing.':
            u'Зачекайте, надсилання триває.',
            u'Buy another ticket?': u'Купити ще один квиток?',
            Localizer.WAIT_FOR_A_TICKET:
            u'Чекайте квиток від %s.' % PHONE_NUMBER,
            u'Bye.': u'До побачення.',
            u'Select a transport.': u'Виберіть вид транспорту.',
            u'Select a route.': u'Виберіть маршрут.',
        }

    def __call__(self, string):
        if self._lang is Localizer.UA:
            return self._ua_strings.get(string, string)
        else:
            return string


class DB:
    '''Manages the database'''

    DB_PATH = 'e:\\data\\python\\resources\\mobile_ticket\\mobtick.bd'

    def __init__(self):
        self._last_err_msg = ''
        self._data = []

    def _check_db_file(self):
        return os.path.exists(DB.DB_PATH) and os.path.isfile(DB.DB_PATH)

    def get_last_err_msg(self):
        return self._last_err_msg

    def get_help(self):
        return u'''The DB is a file in the %s directory.
Each line in the file must be like this:
transport type,transport code,rote 1,route 2,...,route N
Example:
tram,SAC,1,2,3,4,5,6
The DB file should be shipped with the application.
''' % (os.path.dirname(DB.DB_PATH))

    def connect(self):
        if not self._check_db_file():
            emsg = u'The DB file %s is not found. ' +\
                   u'See console output for more info.'
            emsg = emsg % DB.DB_PATH
            self._last_err_msg = emsg
            return False
        f = open(DB.DB_PATH, 'r')
        for line in f.readlines():
            if line.startswith('#'):
                continue
            lst = line.strip().split(',')
            self._data.append({'type': unicode(lst[0], 'UTF-8'),
                               'code': unicode(lst[1]),
                               'routes': [unicode(x) for x in lst[2:]]})
        f.close()
        return True

    def disconnect(self):
        # nothing to do here
        pass

    def get_transport_types(self):
        return [e['type'] for e in self._data]

    def get_routes(self, transport_type):
        r = [e for e in self._data if e['type'] == transport_type][0]['routes']
        return r

    def get_code(self, transport_type):
        c = [e for e in self._data if e['type'] == transport_type][0]['code']
        return c


class Listbox():
    '''Extends appuifw Listbox'''

    def __init__(self, init_list, cb_handler):
        self._lst = init_list
        self._ui_list = appuifw.Listbox(self._lst, cb_handler)
        # bind the handler to key 5
        self._ui_list.bind(0x35, cb_handler)
        # bind the handler to key 2
        self._ui_list.bind(0x32, self.cb_focus_up)
        # bind the handler to key 8
        self._ui_list.bind(0x38, self.cb_focus_down)

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

    @staticmethod
    def compose_txt(code, route):
        return '%s%s' % (code, route)

    @staticmethod
    def send(msg):
        messaging.sms_send(PHONE_NUMBER, msg, callback=None, name="e-ticket")


class MobileTicket:
    '''Mobile ticket.'''

    def __init__(self):
        appuifw.app.screen = "normal"
        appuifw.app.exit_key_handler = self.quit

        self._db = DB()
        if not self._db.connect():
            appuifw.note(self._db.get_last_err_msg(), 'error')
            assert 0, self._db.get_help()
        self._body = None
        self._loc = Localizer(Localizer.UA)

    def _set_list_body(self):
        lst = Listbox(self._db.get_transport_types(), self.at_list_handler)
        appuifw.app.title = self._loc(Localizer.MOBILE_TICKET)
        appuifw.app.body = lst.get_body()
        appuifw.app.menu = [
                    (self._loc(u'Select'), self.at_list_handler),
                    (self._loc(u'Get a duplicate'), self.at_get_dublicate),
                    (self._loc(u'Help'), self.at_help),
                    (self._loc(u'Info'), self.about),
                ]
        self._body = lst

    def _send_request(self, msg):
        i = appuifw.InfoPopup()
        i.show(self._loc(u'Please wait, sending is ongoing.'),
               (0, 0),
               60000,
               0,
               appuifw.EHRightVCenter)
        SMS.send(msg)
        i.hide()

    def run(self):
        self._set_list_body()
        self._script_lock = e32.Ao_lock()
        self._script_lock.wait()

    def at_list_handler(self):
        trans_type = self._body.current_item()
        routes = self._db.get_routes(trans_type)
        idx = appuifw.selection_list(routes, search_field=1)
        if idx is not None:
            self._send_request(SMS.compose_txt(self._db.get_code(trans_type),
                                               routes[idx]))
            msg1 = self._loc(Localizer.WAIT_FOR_A_TICKET)
            msg2 = self._loc(u'Buy another ticket?')
            if not appuifw.query(u'%s\n%s' % (msg1, msg2), "query"):
                appuifw.note(self._loc(u'Bye.'))
                self.quit()

    def at_get_dublicate(self):
        self._send_request(u"D")
        msg1 = self._loc(Localizer.WAIT_FOR_A_TICKET)
        msg2 = self._loc(u'Bye.')
        appuifw.note(u'%s\n%s' % (msg1, msg2))
        self.quit()

    def at_help(self):
        msg1 = self._loc(u'Select a transport.')
        msg2 = self._loc(u'Select a route.')
        msg3 = self._loc(Localizer.WAIT_FOR_A_TICKET)
        appuifw.note(u'1. %s\n2. %s\n3. %s' % (msg1, msg2, msg3), 'info')

    def about(self):
        appuifw.note(u'%s v.%s' % (self._loc(Localizer.MOBILE_TICKET),
                                   __version__),
                     'info')

    def quit(self):
        self._db.disconnect()
        appuifw.app.exit_key_handler = None
        self._script_lock.signal()


if __name__ == '__main__':
    MobileTicket().run()
