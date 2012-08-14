import logging, os
from contextlib import contextmanager
from .deps import serial, xbee
from serial.tools import list_ports
from . import Config, protocol

log = logging.getLogger('xh.SetupUtil')



# ignore in finding Serial ports
EXCLUDE_DEVICES = set([
	'Bluetooth',
	'-COM',
])
def GetSerialCandidates(excludeDevices=EXCLUDE_DEVICES):
	candidates = [d[0] for d in list_ports.comports()
		if all([e not in d[0] for e in excludeDevices])]
	if not candidates:
		raise RuntimeError('No candidates for serial devices found.')
	return candidates


def PickSerialDevice():
	serialDevices = GetSerialCandidates()
	log.debug('Found serial devices: %s' % serialDevices)
	if len(serialDevices) > 1:
		print 'Select serial device:'
		for i, device in enumerate(serialDevices):
			print '[%d]\t%s' % (i, device)
		iStr = raw_input('Number: ')
		i = int(iStr)
	else:
		i = 0
	return serialDevices[i]


@contextmanager
def InitializedXbee(serialDevice=None, callback=None):
	"""
	@param callback called with parsed response/data frames
	"""
	device = serialDevice or PickSerialDevice()
	serialObj = serial.Serial(device, Config.SERIAL_BAUD)

	def parseFrame(rawData):
		frame = protocol.ParseFromDictSafe(rawData)
		if frame and callback:
			try:
				callback(frame)
			except:
				log.error(('error in callback %s handling %s '
				+ '(parsed successfully from %s)')
				% (callback, frame, rawData),
				exc_info=True)

	xb = xbee.ZigBee(serialObj, callback=parseFrame)

	try:
		yield xb
	except KeyboardInterrupt as e:
		log.info('got Ctl-C')
	except Exception as e:
		log.error(e.message, exc_info=True)
	finally:
		xb.halt()
		serialObj.close()


def RunPythonStartup():
	"""
	Run the $PYTHONSTARTUP script, if available, to prepare for an
	interactive prompt.
	"""
	startup = os.getenv('PYTHONSTARTUP')
	if startup:
		execfile(startup)

