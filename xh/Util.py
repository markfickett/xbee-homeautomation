import logging
from .deps import serial, xbee
from serial.tools import list_ports
from . import Config
from contextlib import contextmanager

log = logging.getLogger('xh.Util')



def InvertedDict(d):
	return dict([(v, k) for k, v in d.iteritems()])


def InvertedDictWithRepeatedValues(d):
	"""
	@return a dict where each value in the original maps to a tuple of the
		values in the original map which mapped to it
	"""
	o = {}
	for k, v in d.iteritems():
		keys = o.get(v, ())
		keys = keys + (k,)
		o[v] = keys
	return o


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
	device = serialDevice or PickSerialDevice()
	serialObj = serial.Serial(device, Config.SERIAL_BAUD)
	xb = xbee.ZigBee(serialObj, callback=callback)

	try:
		yield xb
	except KeyboardInterrupt as e:
		log.info('got Ctl-C')
	except Exception as e:
		log.error(e.message, exc_info=True)
	finally:
		xb.halt()
		serialObj.close()

