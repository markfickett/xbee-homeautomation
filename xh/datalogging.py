"""
Write named data values to rotating csv files.
"""
import datetime
import logging
import logging.handlers
import os
import re

from .protocol import PIN
from . import Config, signals


statusLog = logging.getLogger('DataLogging')

# Ex: '2012 Jun 17 23:24:18 UTC'
DATETIME_FORMAT = '%Y %b %d %H:%M:%S UTC'
_FILE_NAME_T = os.path.join(Config.DATA_DIR, 'datalog-%s.csv')
_FILE_NAME_RE = re.compile(_FILE_NAME_T % '(.*)')


def logPinValue(serial, timestamp, pinName, value):
	"""
	Log a pin's sample value.
	"""
	serialStr = formatSerial(serial)
	if pinName not in PIN:
		raise ValueError()
	name = '%s-%s' % (serialStr, str(pinName))
	log(name, timestamp, value=value, serial=serial, pinName=pinName)


def log(name, timestamp, value=None, pinName=None, serial=None):
	"""
	Write a timestamp or timestamped value to a named data log file.

	A DATA_LOGGED signal is sent. If the value or extra keyword arguments
	pinName and serial are included, they are sent with the signal.
	"""
	_getLogger().log(name, timestamp, value=value,
			pinName=pinName, serial=serial)


def formatTimestamp(timestamp):
	return datetime.datetime.strftime(timestamp, DATETIME_FORMAT)


def parseTimestamp(timestampStr):
	return datetime.datetime.strptime(timestampStr, DATETIME_FORMAT)


def formatSerial(serial):
	"""
	Pretty-print an XBee serial number as a 16-character hex string.
	"""
	return '0x%016x' % serial


def getLogFileNames():
	"""
	@return a map of dataset names to absolute path of existing log files.
	"""
	datasetToLogFileName = {}
	if not os.path.isdir(Config.DATA_DIR):
		return datasetToLogFileName
	dataFileNames = [os.path.join(Config.DATA_DIR, fileName)
			for fileName in os.listdir(Config.DATA_DIR)]
	for fileName in dataFileNames:
		match = _FILE_NAME_RE.match(fileName)
		if match:
			datasetToLogFileName[match.group(1)] = fileName
	return datasetToLogFileName


def parseLogFile(logFile):
	"""
	@param logFile an open file (or other like object)
	@return a list of (datetime, string value or None) tuples, in
		chronological order (oldest first)
	"""
	logData = []
	for line in logFile:
		lineData = list(line.strip().split(','))
		lineData[0] = parseTimestamp(lineData[0])
		if len(lineData) < 2:
			lineData.append(None)
		logData.append(tuple(lineData))
	return logData


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


	def __init__(self):
		self.__loggers = {}
		statusLog.debug('will log data to %s', _FILE_NAME_T)
		if not os.path.isdir(Config.DATA_DIR):
			statusLog.debug('creating %s', Config.DATA_DIR)
			os.makedirs(Config.DATA_DIR)


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
				_FILE_NAME_T % name,
				maxBytes=self._MAX_BYTES_PER_LOGFILE,
				backupCount=self._MAX_FILES_PER_NAME)
			dataLog.addHandler(handler)
			self.__loggers[name] = dataLog
		return dataLog


	def log(self, name, timestamp, value=None,
			pinName=None, serial=None):
		formattedTimestamp = formatTimestamp(timestamp)
		if value is None:
			statusLog.debug('%s %s', name, formattedTimestamp)
			self._getLogger(name).info(formattedTimestamp)
			formattedValue = None
		else:
			formattedValue = str(value)
			statusLog.debug('%s %s %s', name,
					formattedTimestamp, formattedValue)
			self._getLogger(name).info('%s,%s',
					formattedTimestamp, formattedValue)
		responses = signals.DATA_LOGGED.send_robust(sender=None,
			name=name,
			value=value,
			formattedValue=formattedValue,
			timestamp=timestamp,
			formattedTimestamp=formattedTimestamp,
			pinName=pinName,
			serial=serial,
		)
		signals.logErrors(responses)

