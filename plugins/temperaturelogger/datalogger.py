import logging

import xh
import locations


log = logging.getLogger('DataLogger')



class DataLogger:
	"""
	Write named data values to rotating csv files.
	"""
	MAX_BYTES_PER_LOGFILE = 5 * 1024 * 1024 # 5MB
	MAX_FILES_PER_NAME = 100


	def __init__(self):
		self.__loggers = {}
		log.debug('will log data to %s', locations.FILE_NAME_T)


	def getLogger(self, name):
		"""
		Get a named logger which writes (samples) to a file.
		"""
		dataLog = self.__loggers.get(name)
		if dataLog is None:
			dataLog = logging.getLogger(name)
			handler = logging.handlers.RotatingFileHandler(
				locations.FILE_NAME_T % name,
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

