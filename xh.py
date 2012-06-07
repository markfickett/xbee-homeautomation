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

def getSerialCandidates():
	candidates = []
	if sys.platform == 'darwin':
		# Expect paths like:
		#	/dev/tty.usbserial-AH01D4Q3 # Sparkfun XBee USB dongle
		#	/dev/tty.usbmodemfa141 # Arduino Uno
		#	/dev/tty.usbserial-A600dSBW # Sparkfun USB FTDI adapter
		basePath = '/dev'
		for device in os.listdir(basePath):
			if (device.startswith('tty.usbserial') or
					device.startswith('tty.usbmodem')):
				candidates.append(os.path.join(
					basePath, device))
	else:
		raise RuntimeError(('Likely candidates for serial devices on'
			+ ' platform "%s" not known. Could not get serial'
			+ ' device candidates.') % sys.platform)
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

def logData(data):
	log.info('data from XBee:\n%s' % data)

try:
	xb = None
	serialDevice = pickSerialDevice()
	s = serial.Serial(serialDevice, Config.SERIAL_BAUD)
	xb = xbee.XBee(s, callback=logData)
	log.info('Created XBee object.')
	for i, cmd in enumerate(['MY', 'ID']):
		frameId = '%X' % i
		log.info('Sending %s with frame ID %s' % (cmd, frameId))
		xb.at(command=cmd, frame_id=frameId)
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
