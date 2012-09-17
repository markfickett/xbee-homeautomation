"""
Write named data values to rotating csv files.
"""
import datetime
import logging
import logging.handlers
import os

from .protocol import PIN
from . import Config, signals


statusLog = logging.getLogger('DataLogging')

# Ex: '2012 Jun 17 23:24:18 UTC'
DATETIME_FORMAT = '%Y %b %d %H:%M:%S UTC'


def logPinValue(serial, pinName, value, timestamp=None):
	"""
	Log a pin's sample value.
	"""
	serialStr = formatSerial(serial)
	if pinName not in PIN:
		raise ValueError()
	log('%s-%s' % (serialStr, str(pinName)), value, timestamp=timestamp,
			serial=serial, pinName=pinName)


def log(name, value, timestamp=None, pinName=None, serial=None):
	"""
	Write a timestamped value to a named data log file.
	@param timestamp a datetime.datetime, defaulting to utcnow()

	A DATA_LOGGED signal is sent when the value is logged. If the extra
	keyword arguments pinName and serial are included, they are sent with
	the signal.
	"""
	_getLogger().log(name, value, timestamp=timestamp, **kwargs)


def formatTimestamp(timestamp):
	return datetime.datetime.strftime(timestamp, DATETIME_FORMAT)


def formatSerial(serial):
	"""
	Pretty-print an XBee serial number as a 16-character hex string.
	"""
	return '0x%016x' % serial


global _dataLoggerSingleton
_dataLoggerSingleton = None
def _getLogger():
	global _dataLoggerSingleton
	if _dataLoggerSingleton is None:
		statusLog.debug('creating data logger')
		_dataLoggerSingleton = _DataLogger()
	return _dataLoggerSingleton



class _DataLogger:
	_MAX_BYTES_PER_LOGFILE = 5 * 1024 * 1024 # 5MB
	_MAX_FILES_PER_NAME = 100
	_FILE_NAME_T = os.path.join(Config.DATA_DIR, 'datalog-%s.csv')


	def __init__(self):
		self.__loggers = {}
		statusLog.debug('will log data to %s', self._FILE_NAME_T)


	def _getLogger(self, name):
		"""
		Get a named logger which writes (samples) to a file.
		"""
		dataLog = self.__loggers.get(name)
		if dataLog is None:
			dataLog = logging.getLogger(name)

			# Do not propagate to root logger which
			# has the default handler and prints to stdout.
			dataLog.propagate = False

			handler = logging.handlers.RotatingFileHandler(
				self._FILE_NAME_T % name,
				maxBytes=self._MAX_BYTES_PER_LOGFILE,
				backupCount=self._MAX_FILES_PER_NAME)
			dataLog.addHandler(handler)
			self.__loggers[name] = dataLog
		return dataLog


	def log(self, name, value, timestamp=None,
			pinName=None, serial=None):
		t = timestamp or datetime.datetime.utcnow()
		formattedTime = formatTimestamp(t)
		formattedValue = str(value)
		self._getLogger(name).info('%s,%s',
				formattedTime, formattedValue)
		statusLog.debug('%s %s %s', name, formattedTime, formattedValue)
		signals.DATA_LOGGED.send(
			name=name,
			value=value,
			formattedValue=formattedValue,
			timestamp=timestamp,
			formattedTimestamp=formattedTimestamp,
			pinName=pinName,
			serial=serial,
		)

