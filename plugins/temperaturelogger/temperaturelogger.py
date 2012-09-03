import datetime
import logging
import logging.handlers
import os
import threading

import xh
from xh.protocol import PIN

from datalogger import DataLogger

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
		if p in (PIN.AD0, PIN.AD1, PIN.AD2, PIN.AD3):
			value = self.__voltsToF(sample.getVolts())
			name = name + '-F'
		elif p is PIN.VCC:
			value = sample.getVolts()
		else:
			raise RuntimeError(('%s plugin not configured to handle'
				+ ' pin %s from module 0x%x.')
				% (self.__class__.__name__, p, sourceSerial))
		self.__recordValue(sourceSerial, timestamp, name, value)


	def __recordValue(self, sourceSerial, timestamp, textName, value):
		name = '0x%x-%s' % (sourceSerial, textName)
		log.debug('%s\t%s\t%.3f'
			% (xh.protocol.Data.FormatTimestamp(timestamp),
				name, value))
		self.__dataLogger.recordValue(name, timestamp, value)


