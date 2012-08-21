"""
methods to be used in setting up Xbee communication or user interaction
"""


import logging, os, readline, traceback
from contextlib import contextmanager
from .deps import serial, xbee
from serial.tools import list_ports
from . import Config, Signals, protocol
from yapsy.PluginManager import PluginManagerSingleton

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


global PluginsCollected
PluginsCollected = False
def CollectPlugins():
	global PluginsCollected
	if not PluginsCollected:
		PluginsCollected = True
		pm = PluginManagerSingleton.get()
		pm.setPluginPlaces([Config.PLUGIN_DIR])
		pm.setPluginInfoExtension(Config.PLUGIN_INFO_EXTENSION)
		pm.collectPlugins()


def _IsErrorTuple(o):
	return (isinstance(o, tuple)
		and len(o) == 3
		and type(o[0]) == type)


@contextmanager
def InitializedXbee(serialDevice=None):
	"""
	Open a serial connection to the locally attached Xbee return an xbee API
	object representing the module, for sending frames.

	A Signals.FRAME_RECEIVED signal will be sent when a frame is received.
	"""
	device = serialDevice or PickSerialDevice()
	serialObj = serial.Serial(device, Config.SERIAL_BAUD)

	def parseFrameAndSendSignal(rawData):
		frame = protocol.ParseFromDictSafe(rawData)
		if frame:
			responses = Signals.FrameReceived.send_robust(
					sender=None, frame=frame)
			for receiver, responseOrErr in responses:
				if not _IsErrorTuple(responseOrErr):
					continue
				formatted = ''.join(traceback.
					format_exception(*responseOrErr))
				log.error(('error in receiver %s handling %s '
				+ '(parsed successfully from %s):\n%s')
				% (receiver, frame, rawData, formatted))

	xb = xbee.ZigBee(serialObj, callback=parseFrameAndSendSignal)

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


def SetLoggerRedisplayAfterEmit(loggerInst):
	"""
	Make the given logger('s last Handler) call readline.redisplay() after
	every emit() call, so that logging plays (sort of) nicely with an
	interactive prompt.
	"""
	handler = loggerInst.handlers[-1]
	oldEmitFn = handler.emit
	def newEmitFn(*args, **kwargs):
		oldEmitFn(*args, **kwargs)
		readline.redisplay()
	handler.emit = newEmitFn


