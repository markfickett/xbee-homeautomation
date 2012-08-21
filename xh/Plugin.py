from yapsy.IPlugin import IPlugin
from . import Signals



class Plugin(IPlugin):
	"""
	Base class that all xh plugins must inherit.
	"""

	def __init__(self, receiveFrames=False):
		"""
		@param receiveFrames If True, register to have _frameReceived
			be called.
		"""
		IPlugin.__init__(self)

		if receiveFrames:
			def handleFrameCb(sender=None, signal=None, frame=None):
				self._frameReceived(frame)
			Signals.FrameReceived.connect(handleFrameCb)
			self.__handleFrameCb = handleFrameCb


	def _frameReceived(self, frame):
		"""
		Called whenever any Xbee Frame is received, if receiveFrames was
		passed to the Plugin constructor.
		"""
		raise NotImplementedError()

