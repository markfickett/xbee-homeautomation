"""
Write named data values to rotating csv files.
"""
import datetime
import logging
import os

from . import Config


statusLog = logging.getLogger('DataLogging')

# Ex: '2012 Jun 17 23:24:18 UTC'
DATETIME_FORMAT = '%Y %b %d %H:%M:%S UTC'


def log(name, value, timestamp=None):
	"""
	Write a timestamped value to a named data log file.
	@timestamp a datetime.datetime, defaulting to utcnow()
	"""
	_getLogger().log(name, value, timestamp=timestamp)


def formatTimestamp(timestamp):
	return datetime.datetime.strftime(timestamp, DATETIME_FORMAT)


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
			handler = logging.handlers.RotatingFileHandler(
				self._FILE_NAME_T % name,
				maxBytes=self._MAX_BYTES_PER_LOGFILE,
				backupCount=self._MAX_FILES_PER_NAME)
			dataLog.addHandler(handler)
			self.__loggers[name] = dataLog
		return dataLog


	def log(self, name, value, timestamp=None):
		formattedTime = formatTimestamp(
			timestamp or datetime.datetime.utcnow())
		self._getLogger(name).info('%s,%s', formattedTime, value)

