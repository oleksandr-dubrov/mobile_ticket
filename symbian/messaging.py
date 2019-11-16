#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

DEBUG = True

def __printd(msg):
	if DEBUG:
		print(msg)


def sms_send(number, msg):
	__printd('Sending {} to {}...'.format(msg, number))
	time.sleep(3.0)
	__printd('done.\n')


ECreated = 0
EMovedToOutBox = 1
EScheduledForSend = 2
ESent = 3# The SMS message has been sent.
EDeleted = 4# The SMS message has been deleted from device's outbox queue. The sms_send operation has finalized and subsequent SMS sending is possible. 
EScheduleFailed = 5
ESendFailed = 6 # This state information is returned when the SMS subsystem has tried to send the message several times in vain. The sms_send operation has finalized and subsequent SMS sending is possible. 
ENoServiceCentre = 7 #This state information is returned by the SMS subsystem in S60 3.x emulator. In emulator this indicates that the sms_send operation has finalized and subsequent SMS sending is possible. 
EFatalServerError = 8
