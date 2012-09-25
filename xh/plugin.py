import logging

from yapsy.IPlugin import IPlugin
from yapsy.PluginManager import PluginManagerSingleton

from . import Config, signals

log = logging.getLogger('Plugin')



class Plugin(IPlugin):
	"""
	Base class that all xh plugins must inherit.
	"""


	def __init__(self, receiveFrames=False):
		"""
		Set up internal state, read configuration, etc.
		@param receiveFrames If True, register to have _frameReceived
			be called.
		"""
		IPlugin.__init__(self)

		self.__receiveFrames = bool(receiveFrames)


	def activate(self):
		"""
		Start doing things: connect to signals, send commands, etc.
		"""
		IPlugin.activate(self)
		if self.__receiveFrames:
			def handleFrameCb(sender=None, signal=None, frame=None):
				self._frameReceived(frame)
			signals.FRAME_RECEIVED.connect(handleFrameCb)
			self.__handleFrameCb = handleFrameCb


	@staticmethod
	def _getConfig():
		"""
		@return the common ConfigParser object for settings/preferences
		"""
		return Config.get()


	def _getConfigSection(self):
		"""
		@return the config section name for this plugin
		"""
		return 'xh.plugin.%s' % self.__class__.__name__


	def getPluginObjByName(self, otherPluginName):
		"""
		Get (the xh.Plugin object for) another plugin, specified by
		name as it appears in that plugin's config file.
		"""
		manager = PluginManagerSingleton.get()
		pluginInfo = manager.getPluginByName(otherPluginName)
		if not pluginInfo:
			raise ValueError(
				'No plugin %r. Available plugins are %s.'
				% (otherPluginName,
				[p.name for p in manager.getAllPlugins()]))
		return pluginInfo.plugin_object


	def _frameReceived(self, frame):
		"""
		Called whenever any Xbee Frame is received, if receiveFrames was
		passed to the Plugin constructor.
		"""
		raise NotImplementedError()

