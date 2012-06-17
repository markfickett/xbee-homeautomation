import logging
log = logging.getLogger('xh.protocol.Command')

from ..deps import Enum
from .. import Encoding, EnumUtil
from . import Frame
import xh.protocol
import threading



class Command(Frame):
	# The fields expected to be in a command dict.
	FIELD = Enum(
		# sequence; stringified number
		'frame_id',

		# command name; ascii
		'command',

		# value sent with or received from command; packed number
		'parameter',

		# status code; packed number
		'status',
	)


	# Recognized command names (alphabetized).
	NAME = Enum(
		'%V', # InputVolts (voltage level on Vcc pin)
		'EE', # encryption enable (0 or 1)
		'ID', # network id
		'KY', # xh.Encoding.NumberToString(xh.Config.LINK_KEY)
		'MY', # node's network ID (0 for coordinator)
		'ND', # NodeDiscover
		'NI', # string node name
		'NT', # discover timeout
		'SH', # serial (high bits)
		'SL', # serial (low bits)
		'WR', # write configuration to non-volatile memory
	)


	# Response status.
	STATUS = Enum(
		'OK',			# must be index 0
		'ERROR',		# 1
		'INVALID_COMMAND',	# 2
		'INVALID_PARAMETER',	# 3
		'TRANSMIT_FAILURE',	# 4
	)


	# Next unclaimed frame ID for a command to send.
	__sendingFrameId = 0
	__frameIdLock = threading.Lock()


	def __init__(self, name, frameId=None):
		Frame.__init__(self)

		if frameId is None:
			with Command.__frameIdLock:
				self.__frameId = Command.__sendingFrameId
				Command.__sendingFrameId += 1
		else:
			self.__frameId = int(frameId)

		if name not in Command.NAME:
			raise ValueError('Name "%s" not in NAME enum.' % name)
		self.__name = name
		self.__parameter = None
		self.setStatus(None)


	def getFrameId(self):
		return self.__frameId


	def getName(self):
		return self.__name


	def setStatus(self, status):
		if not (status is None or status in Command.STATUS):
			raise ValueError(
				'Status "%s" not None or in STATUS enum.'
				% status)
		self.__status = status


	def getStatus(self):
		return self.__status


	def setParameter(self, parameter):
		self.__parameter = parameter


	def getParameter(self):
		return self.__parameter


	def __str__(self):
		status = self.getStatus()
		d = {
			'name': self.getName(),
			'id': self.getFrameId(),
			'status': status and (' (%s)' % status) or '',
			'param': self._formatParameter(),
		}
		return '#%(id)d %(name)s%(status)s%(param)s' % d


	def _formatParameter(self):
		"""
		Format the parameter (or its parsed value(s)) for __str__.
		"""
		return self._FormatNamedValues(
			{'parameter': self.getParameter()})


	def mergeFromDict(self, d):
		"""
		Parse status, parameter, and any class-specific fields from a
		response dict.
		@return a set of the keys used
		"""
		usedKeys = set()

		statusKey = str(Command.FIELD.status)
		status = d.get(statusKey)
		if status is not None:
			status = Command.STATUS[Encoding.StringToNumber(status)]
			self.setStatus(status)
			usedKeys.add(statusKey)

		paramKey = str(Command.FIELD.parameter)
		parameter = d.get(paramKey)
		if parameter is not None:
			self.parseParameter(parameter)
			usedKeys.add(paramKey)

		return usedKeys


	def parseParameter(self, encoded):
		n = self.getName()
		self.setParameter(self._parseParameterDefault(encoded))


	def _parseParameterDefault(self, encoded):
		"""
		By default, parse a parameter as a packed number. Warn if the
		command may not actually have a numeric parameter.
		@return The parameter parsed as a number.
		"""
		parameter = Encoding.StringToNumber(encoded)
		if self.getName() not in (
			Command.NAME.__getattribute__('%V'),
			Command.NAME.ID,
			Command.NAME.MY,
			Command.NAME.NI,
			Command.NAME.NT,
			Command.NAME.SH,
			Command.NAME.SL,
		):
			log.warning(('uncertain conversion of encoded parameter'
				+ ' "%s" to number 0x%X for command %s')
				% (encoded, parameter, self.getName()))
		return parameter


	def send(self, xb):
		log.info('sending %s' % self)
		xb.at(command=str(self.getName()),
			frame_id=self._encodedFrameId(),
			parameter=self._encodedParameter())


	def _encodedFrameId(self):
		return Encoding.NumberToPrintedString(self.getFrameId())


	def _encodedParameter(self):
		return Encoding.NumberToString(self.getParameter())



class _CommandRegistry:
	def __init__(self):
		self.__registry = {}


	@staticmethod
	def _CheckName(name):
		if name not in Command.NAME:
			raise ValueError(('Name "%s" not in the Command.NAME'
				+ ' enum.') % name)


	def put(self, name, commandClass):
		"""
		Register a command subclass to be autocreated for
		a given command.
		"""
		if name in self.__registry:
			raise RuntimeError(('Command registry already has an '
				+ 'entry for %s: %s.')
				% (name, self.__registry[name]))
		self.__registry[name] = commandClass


	def get(self, name):
		self._CheckName(name)
		return self.__registry.get(name)



CommandRegistry = _CommandRegistry()
