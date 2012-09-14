import logging
import threading

import xh
from xh.protocol import Command

log = logging.getLogger('Presence')



class Presence(xh.Plugin):
	"""
	Maintain a directory of which XBee modules (known by serial number) are
	available.

	Since no frame is sent when a node leaves the network, and in the
	absence of polling, the directory naively contains all nodes ever seen.
	The plugin listens for both explicitly presence-related frames (NodeId
	and NodeDiscover) and select implicit indications (Data frames).

	All public methods are thread-safe.
	"""


	def __init__(self):
		xh.Plugin.__init__(self, receiveFrames=True)
		self.__lock = threading.Lock()
		self.__serials = set()
		self.__localSerial = None


	def getRemoteSerials(self):
		"""
		Get a set of the serial numbers of all known remote XBees.
		"""
		with self.__lock:
			return set(self.__serials)


	def getLocalSerial(self):
		"""
		Get the serial number of the local XBee (likely the
		coordinator), or None if it has not been retrieved.
		"""
		with self.__lock:
			return self.__localSerial


	def activate(self):
		xh.Plugin.activate(self)

		highBits = xh.synchronous.sendAndWait(
			Command(Command.NAME.SH)).getParameter()
		lowBits = xh.synchronous.sendAndWait(
			Command(Command.NAME.SL)).getParameter()
		with self.__lock:
			self.__localSerial = xh.encoding.buildSerial(
				highBits, lowBits)
		log.debug("retrieved local XBee's serial as %s",
			xh.datalogging.formatSerial(self.__localSerial))

		xh.protocol.NodeDiscover().send()


	def _frameReceived(self, frame):
		serial = None
		if isinstance(frame, xh.protocol.NodeDiscover):
			serial = frame.getNodeId().getSerial()
		elif isinstance(frame, xh.protocol.NodeId):
			serial = frame.getSerial()
		elif hasattr(frame, 'getSourceAddressLong'):
			serial = frame.getSourceAddressLong()

		with self.__lock:
			if serial is not None and serial not in self.__serials:
				log.debug('now present: %s',
					xh.datalogging.formatSerial(serial))
				self.__serials.add(serial)


