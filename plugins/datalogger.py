import logging
import threading

import xh
from xh.protocol import Command, PIN


log = logging.getLogger('DataLogger')



class DataLogger(xh.Plugin):
	"""
	Log the data from all frames using xh.datalogging.

	Data includes samples (automatically sent or via InputSample) and
	supply voltages (via InputVolts). Data is logged raw (in volts or as
	boolean values).

	InputVolts is actively queried.
	"""
	_PRESENCE_PLUGIN_NAME = 'Presence'
	_POLL_INTERVAL_SEC = 5 * 60.0


	def __init__(self):
		xh.Plugin.__init__(self, receiveFrames=True)


	def activate(self):
		xh.Plugin.activate(self)
		self.__presence = self.getPluginObjByName(
			self._PRESENCE_PLUGIN_NAME)
		self.__poll()


	def _frameReceived(self, frame):
		if isinstance(frame, xh.protocol.Data):
			self.__logData(frame)
		elif isinstance(frame, xh.protocol.InputSample):
			self.__logInputSample(frame)
		elif isinstance(frame, xh.protocol.InputVolts):
			self.__logInputVolts(frame)


	def __logData(self, frame):
		serial = (frame.getSourceAddressLong()
			or self.__presence.getLocalSerial())
		t = frame.getTimestamp()
		for sample in frame.getSamples():
			xh.datalogging.logPinValue(serial, t,
				sample.getPinName(), sample.getValue())


	def __logInputSample(self, frame):
		serial = (frame.getRemoteSerial()
			or self.__presence.getLocalSerial())
		for sample in frame.getSamples():
			xh.datalogging.logPinValue(serial, frame.getTimestamp(),
				sample.getPinName(), sample.getValue())


	def __logInputVolts(self, frame):
		serial = (frame.getRemoteSerial()
			or self.__presence.getLocalSerial())
		v = frame.getVolts()
		t = frame.getTimestamp()
		xh.datalogging.logPinValue(serial, t, PIN.VCC, v)


	def __poll(self):
		"""
		At a set interval, poll for data values which are not
		automatically sent.

		Work around a bug in xbee-python's parsing of Vcc voltages (see
		xh.protocol.data.VCC_BUG_URL) by actively polling supply
		voltage level.
		"""
		thread = threading.Timer(self._POLL_INTERVAL_SEC, self.__poll)
		thread.daemon = True
		thread.start()
		for serial in self.__presence.getRemoteSerials():
			xh.protocol.InputVolts(dest=serial).send()


