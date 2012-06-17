#!/usr/bin/python
"""%prog command [options]
Issue commands to or read data from the XBee Home Automation system.
Examples:
 $ xh info # print information about a physically connected XBee
 $ xh init # initialize network PANID and encryption key
 $ xh setup --name 'Living Room' # set up and name a new sensor/control
"""

import logging
log = logging.getLogger('xh')

import sys, os, time, optparse
import xh
from xh.protocol import Command, NodeDiscover
from xh.deps import serial, xbee

from serial.tools import list_ports
EXCLUDE_DEVICES = 'Bluetooth' # ignore in finding Serial ports

def getSerialCandidates():
	candidates = [d[0] for d in list_ports.comports()
		if EXCLUDE_DEVICES not in d[0]]
	if not candidates:
		raise RuntimeError('No candidates for serial devices found.')
	return candidates

def pickSerialDevice():
	serialDevices = getSerialCandidates()
	log.info('Found serial devices: %s' % serialDevices)
	if len(serialDevices) > 1:
		print 'Select serial device:'
		for i, device in enumerate(serialDevices):
			print '%d\t%s' % (i, device)
		iStr = raw_input('Number: ')
		i = int(iStr)
	else:
		i = 0
	return serialDevices[i]

log.info('started')
log.info('Type control-C to exit.')

def logData(rawData):
	try:
		command = xh.protocol.ParseCommandFromDict(rawData)
		log.info('received %s' % command)
	except:
		log.error('could not deal with data', exc_info=True)

try:
	xb = None
	serialDevice = pickSerialDevice()
	s = serial.Serial(serialDevice, xh.Config.SERIAL_BAUD)
	xb = xbee.XBee(s, callback=logData)
	log.info('Created XBee object.')
	for cmd in (
		Command(Command.NAME.MY),
		Command(Command.NAME.ID),
		Command(Command.NAME.KY),
		Command(Command.NAME.EE),
		Command(Command.NAME.SH),
		Command(Command.NAME.SL),
		Command(Command.NAME.NI),
		Command(Command.NAME.__getattribute__('%V')),
		Command(Command.NAME.NT),
		NodeDiscover(),
	):
		cmd.send(xb)
	while True:
		time.sleep(0.02)
except KeyboardInterrupt as e:
	log.info('Got ^C.')
except Exception as e:
	log.error(e.message, exc_info=True)
finally:
	if xb:
		xb.halt()

log.info('exiting')
