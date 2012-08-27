import datetime
import logging
import logging.handlers
import os
import threading

import xh
from xh.protocol import PIN

log = logging.getLogger('TemperatureLogger')



class TemperatureLogger(xh.Plugin):
	"""
	Log temperature values from TEMP36 (see
	http://learn.adafruit.com/tmp36-temperature-sensor ).
	"""
	_INPUT_VOLTS_QUERY_INTERVAL_SEC = 5 * 60.0


	def __init__(self):
		xh.Plugin.__init__(self, receiveFrames=True)
		self.__dataLogger = DataLogger()


	def activate(self):
		xh.Plugin.activate(self)
		serials = self.getSerials()
		if serials:
			self.__sendInputVoltsQueryAndRepeat(serials)
		else:
			log.warning(('%s has no associated serials, will not '
			+ 'query for input voltage levels.')
			% self.__class__.__name__)


	def __sendInputVoltsQueryAndRepeat(self, serials):
		"""
		Work around bug in xbee-python's parsing of Vcc voltages (see
		xh.protocol.data.VCC_BUG_URL) by actively polling supply
		voltage level.
		"""
		thread = threading.Timer(self._INPUT_VOLTS_QUERY_INTERVAL_SEC,
			self.__sendInputVoltsQueryAndRepeat, args=[serials,])
		thread.daemon = True
		thread.start()
		for s in serials:
			xh.protocol.InputVolts(dest=s).send()


	def _frameReceived(self, frame):
		"""
		Unpack sample data from frames, converting from device-oriented
		units (voltage) to human-readable units (degrees Fahrenheit).
		"""
		serials = self.getSerials()
		if isinstance(frame, xh.protocol.Data):
			sourceSerial = frame.getSourceAddressLong()
			if sourceSerial not in serials:
				return
			t = frame.getTimestamp()
			for sample in frame.getSamples():
				self.__logSample(sourceSerial, t, sample)
		elif isinstance(frame, xh.protocol.InputVolts):
			sourceSerial = frame.getRemoteSerial()
			if sourceSerial not in serials:
				return
			self.__recordValue(sourceSerial,
				datetime.datetime.utcnow(),
				str(PIN.VCC),
				frame.getVolts())
		elif isinstance(frame, xh.protocol.InputSample):
			sourceSerial = frame.getRemoteSerial()
			if sourceSerial not in serials:
				return
			t = datetime.datetime.utcnow()
			for sample in frame.getSamples():
				self.__logSample(sourceSerial, t, sample)


	@staticmethod
	def __voltsToF(volts):
		return ((volts*100 - 50) * (9.0/5.0) + 32)


	def __logSample(self, sourceSerial, timestamp, sample):
		p = sample.getPinName()
		name = str(p)
		if p in (PIN.AD0, PIN.AD1, PIN.AD2):
			value = self.__voltsToF(sample.getVolts())
		elif p is PIN.VCC:
			value = sample.getVolts()
		else:
			raise RuntimeError(('%s plugin not configured to handle'
				+ ' pin %s from module 0x%x.')
				% (self.__class__.__name__, p, sourceSerial))
		self.__recordValue(sourceSerial, timestamp, name, value)


	def __recordValue(self, sourceSerial, timestamp, textName, value):
		name = '0x%x %s' % (sourceSerial, textName)
		log.info('%s\t%s\t%.3f'
			% (xh.protocol.Data.FormatTimestamp(timestamp),
				name, value))
		self.__dataLogger.recordValue(name, timestamp, value)


class DataLogger:
	"""
	Write named data values to rotating csv files.
	"""
	MAX_BYTES_PER_LOGFILE = 5 * 1024 * 1024 # 5MB
	MAX_FILES_PER_NAME = 100
	DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),
		'..', '..', 'data'))
	FILE_NAME_T = os.path.join(DATA_DIR, 'datalog-%s.csv')


	def __init__(self):
		self.__loggers = {}
		log.debug('will log data to %s', self.FILE_NAME_T)


	def getLogger(self, name):
		"""
		Get a named logger which writes (samples) to a file.
		"""
		dataLog = self.__loggers.get(name)
		if dataLog is None:
			dataLog = logging.getLogger(name)
			handler = logging.handlers.RotatingFileHandler(
				self.FILE_NAME_T % name,
				maxBytes=self.MAX_BYTES_PER_LOGFILE,
				backupCount=self.MAX_FILES_PER_NAME)
			dataLog.addHandler(handler)
			self.__loggers[name] = dataLog
		return dataLog


	def recordValue(self, name, timestamp, value):
		"""
		Write a timestamped value to a named data log file.
		"""
		self.getLogger(name).info('%s,%s',
			xh.protocol.Data.FormatTimestamp(timestamp), value)

