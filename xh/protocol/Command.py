import logging
log = logging.getLogger('xh.protocol.Command')

from xh.deps import Enum
from xh import Encoding, EnumUtil
import xh.protocol
import threading



class Command:
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
		param = self.getParameter()
		if param:
			if type(param) is int:
				param = '0x%X' % param
			return ' parameter=%s' % param
		else:
			return ''


	def mergeFromDict(self, d):
		"""
		Parse status, parameter, and any class-specific fields from a
		response dict.
		"""
		status = d.get(str(Command.FIELD.status))
		if status is not None:
			status = Command.STATUS[Encoding.StringToNumber(status)]
			self.setStatus(status)

		parameter = d.get(str(Command.FIELD.parameter))
		if parameter is not None:
			self.parseParameter(parameter)


	def parseParameter(self, encoded):
		n = self.getName()
		if n is Command.NAME.ND:
			parameter = xh.protocol.ParseNodeDiscover(encoded)
		else:
			parameter = self._parseParameterDefault(encoded)
		self.setParameter(parameter)


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
