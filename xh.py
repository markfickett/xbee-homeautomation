#!/usr/bin/python
"""%prog command [options]
Issue commands to or read data from the XBee Home Automation system.
Examples:
 $ xh info # print information about a physically connected XBee
 $ xh init # initialize network PANID and encryption key
 $ xh setup --name 'Living Room' # set up and name a new sensor/control
"""

from Manifest import logging
log = logging.getLogger('xh')

from Manifest import sys, os, time, optparse, serial, xbee, Config

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

def packNumberInString(n):
	"""
	Pack numbers of arbitrary size into (little-endian) strings.
	Example: 0x3ef7 => '\x3e\xf7'
	"""
	s = ''
	while n > 0:
		lowByte = n % 0x100
		s = chr(lowByte) + s
		n = n / 0x100
	return s

log.info('started')
log.info('Type control-C to exit.')

def logData(data):
	log.info('data from XBee:\n%s' % data)

try:
	xb = None
	serialDevice = pickSerialDevice()
	s = serial.Serial(serialDevice, Config.SERIAL_BAUD)
	xb = xbee.XBee(s, callback=logData)
	log.info('Created XBee object.')
	for i, cmd in enumerate([
		#'MY', # node's network ID (0 for coordinator)
		'ID', # network ID
		#('ID', '\x3E\xF7'), # set network ID to 0x3EF7
		#('KY', '\x32\x10'), # set network key to 0x3210
		#('KY', packNumberInString(Config.LINK_KEY)),
		#'WR', # write network key
		#'EE', # encryption enable (0 or 1)
		#'SH', # serial (high bits)
		#'SL', # serial (low bits)
		#'NI', # string node name
		'%V', # Vcc voltage, value * 1200/1024.0 = mV
		'NT', # discovery timeout
		'ND'] # node discover
	):
		frameId = '%X' % i
		parameter = None
		if type(cmd) is tuple:
			cmd, parameter = cmd
		log.info('Sending %s with frame ID %s%s' %
			(cmd, frameId,
			(parameter and ' and parameter %s' % parameter) or ''))
		xb.at(command=cmd, frame_id=frameId, parameter=parameter)
	while True:
		time.sleep(0.02)
except KeyboardInterrupt, e:
	log.info('Got ^C.')
except Exception, e:
	log.error(e.message, exc_info=True)
finally:
	if xb:
		xb.halt()

log.info('exiting')
