import logging
log = logging.getLogger('xh.protocol.Command')

from ..deps import Enum
from .. import Encoding, EnumUtil
from . import Frame, FrameRegistry, Registry
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

		# 16-bit network address of the responder for remote commands
		'source_addr',

		# 64-bit
		'source_addr_long',
	)


	# Recognized command names (alphabetized).
	NAME = Enum(
		'%V', # InputVolts (voltage level on Vcc pin)
		'EE', # encryption enable (0 or 1)
		'ID', # network id
		'IR', # IO sample rate
		'KY', # xh.Encoding.NumberToString(xh.Config.LINK_KEY)
		'MY', # node's network ID (0 for coordinator)
		'ND', # NodeDiscover
		'NI', # string node name
		'NT', # discover timeout
		'PR', # PullUpResistor (bit field for internal resistors)
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


	def __init__(self, name, responseFrameId=None, dest=None):
		"""
		@param dest 64-bit destination address. If given, this Command
			will be sent to the given remote note.
		"""
		if responseFrameId is None:
			frameType = Frame.TYPE.at
		else:
			frameType = Frame.TYPE.at_response

		if dest is not None:
			if frameType is not Frame.TYPE.at:
				raise ValueError('cannot set dest for response')

		Frame.__init__(self, frameType=frameType)

		self.__remoteNetworkAddress = None
		self.__remoteSerial = None

		if responseFrameId is None:
			with Command.__frameIdLock:
				self.__frameId = Command.__sendingFrameId
				Command.__sendingFrameId += 1
			if dest is not None:
				self.__remoteSerial = int(dest)
		else:
			self.__frameId = int(responseFrameId)

		if name not in Command.NAME:
			raise ValueError('Name "%s" not in NAME enum.' % name)
		self.__name = name
		self.__parameter = None
		self.setStatus(None)


	def getFrameId(self):
		return self.__frameId


	def getName(self):
		return self.__name


	def isRemote(self):
		return self.getRemoteSerial() is not None


	def getRemoteNetworkAddress(self):
		return self.__remoteNetworkAddress


	def getRemoteSerial(self):
		return self.__remoteSerial


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


	def getNamedValues(self, includeParameter=True):
		d = Frame.getNamedValues(self)
		d.update({
			'remoteAddr': self.getRemoteNetworkAddress(),
			'remoteSerial': self.getRemoteSerial(),
		})
		if includeParameter:
			d.update({'parameter': self.getParameter()})
		return d


	def __str__(self):
		status = self.getStatus()
		namedStrings = {
			'id': self.getFrameId(),
			'name': self.getName(),
			'status': status and (' (%s)' % status) or '',
			'param': self._FormatNamedValues(self.getNamedValues()),
		}
		return ('#%(id)d %(name)s%(status)s%(param)s'
			% namedStrings)


	def _updateFromDict(self, d, usedKeys):
		"""
		Parse status, parameter, and any class-specific fields from a
		response dict.
		"""
		Frame._updateFromDict(self, d, usedKeys)

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

		srcKey = str(Command.FIELD.source_addr)
		src = d.get(srcKey)
		if src is not None:
			self.__remoteNetworkAddress = (
				Encoding.StringToNumber(src))
			usedKeys.add(srcKey)

			srcLongKey = str(Command.FIELD.source_addr_long)
			self.__remoteSerial = Encoding.StringToNumber(
				d[srcLongKey])
			usedKeys.add(srcLongKey)


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
		kwargs = {
			'command': str(self.getName()),
			'frame_id': self._encodedFrameId(),
			'parameter': self._encodedParameter(),
		}
		if self.isRemote():
			kwargs['dest_addr_long'] = (
				Encoding.NumberToSerialString(
					self.getRemoteSerial()))
			xb.remote_at(**kwargs)
		else:
			xb.at(**kwargs)


	def _encodedFrameId(self):
		return Encoding.NumberToPrintedString(self.getFrameId())


	def _encodedParameter(self):
		return Encoding.NumberToString(self.getParameter())


	@classmethod
	def _CreateFromDict(cls, d, usedKeys):
		frameIdKey = str(Command.FIELD.frame_id)
		frameId = d.get(frameIdKey)
		frameId = Encoding.PrintedStringToNumber(d[frameIdKey])
		usedKeys.add(frameIdKey)

		nameKey = str(Command.FIELD.command)
		name = d.get(nameKey)
		if name is not None:
			name = EnumUtil.FromString(Command.NAME, name)
			usedKeys.add(nameKey)

		commandClass = CommandRegistry.get(name)
		if commandClass:
			c = commandClass(responseFrameId=frameId)
		else:
			c = Command(name, responseFrameId=frameId)

		return c



CommandRegistry = Registry(Command.NAME)
CommandRegistry.__doc__ = ('Which Command.NAME is to be parsed '
	+ 'by which Command subclass.')



FrameRegistry.put(Frame.TYPE.at_response, Command)
FrameRegistry.put(Frame.TYPE.remote_at_response, Command)
