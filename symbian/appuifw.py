#!/usr/bin/env python
# -*- coding: utf-8 -*-


DBG_MODE = False


def printd(self, *args):
	if DBG_MODE:
		msg = '| log :'
		msg += ' '.join(str(args))
		print msg


class app:
		body = None
		title = None
		screen = None
		exit_key_handler = None
		menu = None


class Text:
	def __init__(self):
		font = None  # @UnusedVariable
		color = None  # @UnusedVariable
		highlight_color = None  # @UnusedVariable

	def set(self, msg):
		print(msg)

	def set_pos(self, pos):
		pass


class Canvas:
	def __init__(self, event_callback=None, redraw_callback=None, resize_callback=None):
		self.size = (240, 234)

	def rectangle(self, coords, fill):
		printd("Rectangle with coodrs (%d, %d, %d, %d) and filled with (%d, %d, %d)" %
			   (coords + fill))

	def line(self, coords, width, outline):
		printd("Line with coords (%d, %d, %d, %d) outlined by (%d, %d, %d)" %
			   (coords + outline))

	def measure_text(self, text, font):
		dummy_coords = ((0, -18, 54, 3),)  # spokij
		printd(u"Measure text %s" % (text))
		printd("Return (%d, %d, %d, %d)" % (dummy_coords[0]))
		return dummy_coords

	def text(self, coords, text, fill, font):
		utext = u''.join(text if text else '')
		printd(u"Print text %s with coords (%d, %d)" % ((utext,) + coords))
		if not utext == ' ':
			print ('	%s' % utext)


class Listbox:
	def __init__(self, lst, handler):
		self.lst = lst
		self.cur_idx = 0

	def bind(self, num, callback):
		pass

	def current(self):
		return self.cur_idx

	def set_list(self, lst, cur_idx):
		self.lst = lst
		self.cur_idx = cur_idx

def note(text, tp):
	print ("Note %s: %s" % (text, tp))


class InfoPopup:
	def __init__(self):
		pass

	def show(self, msg, coords=(), time_shown=5000, time_before=0, alignment=0):  # @UnusedVariable
		print('Show an info pop-up: {} for {} seconds.\n'.format(msg, time_shown))

	def hide(self):
		print('Hide the info pop-up')


def query(msg, tp):
	print (msg)
	if tp == "query":
		o = raw_input('0 - no, 1 - yes.\n')
		if o == '0':
			return 0
		else:
			return 1
	elif tp == "text":
		o = raw_input()
		return unicode(o, 'utf-8')


def selection_list(lst, search_field=0):
	print ('+ Choose an item.')
	for idx in range(len(lst)):
		print ('%d - %s' % (idx, lst[idx]))

	print ('%d - Go to the main menu' % (len(lst)))
	o = raw_input(' -> ')
	try:
		if int(o) == len(lst):
			return None
		elif int(o) > len(lst):
			raise ValueError(o)
		else:
			return int(o)
	except ValueError as e:
		print ('Wrong input: %s' % e)
		return selection_list(lst, search_field=search_field)


def multi_selection_list(lst, style='checkbox', search_field=0):  # @DontTrace
	assert lst and len(lst), 'no list or the list is empty'
	assert len(lst) < 12, 'the list is to long'
	print ('Choose items, separate by comma.')
	for idx in range(len(lst)):
		print ('%d. %s' % (idx, lst[idx]))
	print ('%d - Go to the main menu' % (len(lst)))
	o = raw_input()
	items = o.split(',')
	ret = []
	try:
		for i in items:
			o = int(i.strip())
			if o == len(lst):
				return None
			elif o > len(lst):
				raise ValueError(o)
			else:
				ret.append(o)
	except ValueError as e:
		print ('Wrong input: %s' % e)
		multi_selection_list(lst, style='checkbox', search_field=search_field)
	return ret

def popup_menu(lst):  # @UnusedVariable
	return 0

EKeyLeftSoftkey = 0x01
EKeyYes = 0x02
EKeyMenu = 0x03
EKey0 = 0x04
EKey1 = 0x05
EKey2 = 0x06
EKey3 = 0x07
EKey4 = 0x08
EKey5 = 0x09
EKey6 = 0x10
EKey7 = 0x11
EKey8 = 0x12
EKey9 = 0x13
EKeyStar = 0x14
EKeyLeftArrow = 0x15
EKeyUpArrow = 0x16
EKeySelect = 0x17
EKeyRightArrow = 0x18
EKeyDownArrow = 0x19
EKeyRightSoftkey = 0x20
EKeyNo = 0x21
EKeyBackspace = 0x22
EKeyEdit = 0x23
EKeyHash = 0x24

EScancode0 = 0x30
EScancode1 = 0x31
EScancode2 = 0x32
EScancode3 = 0x33
EScancode4 = 0x34
EScancode5 = 0x35
EScancode6 = 0x36
EScancode7 = 0x37
EScancode8 = 0x38
EScancode9 = 0x39

EEventKey = 0x51


EHLeftVTop = 0
EHLeftVCenter = 1
EHLeftVBottom = 2
EHCenterVTop = 3
EHCenterVCenter = 4
EHCenterVBottom = 5
EHRightVTop = 6
EHRightVCenter = 7
EHRightVBottom = 8

HIGHLIGHT_SHADOW = 0
HIGHLIGHT_ROUNDED = 1
