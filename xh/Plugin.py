from yapsy.IPlugin import IPlugin
from . import Config, Signals
import logging
log = logging.getLogger('Plugin')



class Plugin(IPlugin):
	"""
	Base class that all xh plugins must inherit.
	"""
	__CONFIG_NUM_SERIALS = 'numSerials'
	__CONFIG_SERIAL_T = 'serial%d'


	def __init__(self, receiveFrames=False):
		"""
		@param receiveFrames If True, register to have _frameReceived
			be called.
		"""
		IPlugin.__init__(self)

		self.__receiveFrames = bool(receiveFrames)

		self.clearSerials()
		c = Config.get()
		sec = self._getConfigSection()
		if c.has_section(sec):
			n = c.getint(sec, self.__CONFIG_NUM_SERIALS)
			for i in xrange(n):
				s = c.getint(sec, self.__CONFIG_SERIAL_T % i)
				self.__serials.add(s)


	def activate(self):
		IPlugin.activate(self)
		if self.__receiveFrames:
			def handleFrameCb(sender=None, signal=None, frame=None):
				self._frameReceived(frame)
			Signals.FrameReceived.connect(handleFrameCb)
			self.__handleFrameCb = handleFrameCb


	def _getConfigSection(self):
		return 'xh.plugin.%s' % self.__class__.__name__


	def setSerials(self, serials):
		"""
		@param serials list of Xbee serial numbers which this plugin
			should associate with, stored in config
		"""
		self.__serials = set([int(s) for s in serials])

		c = Config.get()
		sec = self._getConfigSection()
		if not c.has_section(sec):
			c.add_section(sec)
		c.set(sec, self.__CONFIG_NUM_SERIALS, str(len(self.__serials)))
		for i, s in enumerate(self.__serials):
			c.set(sec, self.__CONFIG_SERIAL_T % i, str(s))


	def getSerials(self):
		return set(self.__serials)


	def clearSerials(self):
		self.__serials = set()


	def _frameReceived(self, frame):
		"""
		Called whenever any Xbee Frame is received, if receiveFrames was
		passed to the Plugin constructor.
		"""
		raise NotImplementedError()

