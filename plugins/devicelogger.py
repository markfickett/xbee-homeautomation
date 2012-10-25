import logging

import xh
from xh.protocol import NodeId


log = logging.getLogger('DeviceLogger')


class DeviceLogger(xh.Plugin):
	"""
	Log stats about device (and indirectly, network) behavior.
	"""


	_DATA_INTERVAL = 'data interval'
	_ID_EVENTS = {
		NodeId.EVENT.BUTTON: 'commission button press',
		NodeId.EVENT.JOIN: 'join network',
		NodeId.EVENT.POWER_CYCLE: 'power cycle',
	}


	def __init__(self):
		xh.Plugin.__init__(self, receiveFrames=True)
		self.__prevEvent = {}


	def _frameReceived(self, frame):
		event = None
		if isinstance(frame, xh.protocol.Data):
			name = self._makeName(frame.getSourceAddressLong(),
					self._DATA_INTERVAL)
			self._logInterval(name, frame.getTimestamp())
		if isinstance(frame, NodeId):
			name = self._makeName(frame.getSerial(),
					self._ID_EVENTS[frame.getSourceEvent()])
			self._logOccurrence(name, frame.getTimestamp())

	def _makeName(self, serial, event):
		return '%s-%s' % (xh.datalogging.formatSerial(serial), event)

	def _logInterval(self, name, timestamp):
		prev = self.__prevEvent.get(name)
		self.__prevEvent[name] = timestamp
		if prev is None:
			return
		dt = timestamp - prev
		dtMillis = dt.total_seconds() * 1000
		xh.datalogging.log(name + ' ms', timestamp, dtMillis)

	def _logOccurrence(self, name, timestamp):
		xh.datalogging.log(name, timestamp)

