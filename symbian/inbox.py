#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True

def __printd(msg):
	if DEBUG:
		print(msg)


class Inbox(object):

	def content(self, msg_id):
		msg = 'The content of the message {}\n'.format(msg_id)
		return msg

	def address(self, msg_id):
		print('get address of SMS {}'.format(msg_id))
		return '+123456789'


EInbox = 0 #    The device's inbox folder.
EOutbox = 1 #    The device's outbox folder.
ESent = 2 #    The sent messages folder.
EDraft = 3 #    The draft messages folder.
