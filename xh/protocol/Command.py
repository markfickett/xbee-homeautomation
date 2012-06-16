import logging
log = logging.getLogger('xh.protocol.Command')

from xh.deps import Enum
from xh import Encoding, EnumUtil
import Protocol

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
		'%V',
		'EE',
		'ID',
		'KY',
		'MY',
		'ND',
		'NI',
		'NT',
		'SH',
		'SL',
		'WR',
	)

	# Response status.
	STATUS = Enum(
		'OK',			# must be index 0
		'ERROR',		# 1
		'INVALID_COMMAND',	# 2
		'INVALID_PARAMETER',	# 3
		'TRANSMIT_FAILURE',	# 4
	)

	def __init__(self, frameId, name, status=None):
		self.__frameId = int(frameId)
		if name not in Command.NAME:
			raise ValueError('Name "%s" not in NAME enum.' % name)
		self.__name = name
		if not (status is None or status in Command.STATUS):
			raise ValueError(
				'Status "%s" not None or in STATUS enum.'
				% status)
		self.__status = status
		self.__parameter = None

	def getFrameId(self):
		return self.__frameId

	def getName(self):
		return self.__name

	def getStatus(self):
		return self.__status

	def setParameter(self, parameter):
		self.__parameter = parameter

	def getParameter(self):
		return self.__parameter

	def __str__(self):
		status = self.getStatus()
		param = self.getParameter()
		if type(param) is int:
			param = '0x%X' % param
		d = {
			'name': self.getName(),
			'id': self.getFrameId(),
			'status': status and (' (%s)' % status) or '',
			'param': param and (' parameter=%s' % param) or '',
		}
		return '#%(id)d %(name)s%(status)s%(param)s' % d

	@classmethod
	def ParseFromDict(cls, d):
		frameId = Encoding.PrintedStringToNumber(
			d[str(Command.FIELD.frame_id)])
		name = EnumUtil.FromString(Command.NAME, d['command'])

		status = d.get(str(Command.FIELD.status))
		if status is not None:
			status = Command.STATUS[Encoding.StringToNumber(status)]

		c = Command(frameId, name, status=status)

		parameter = d.get(str(Command.FIELD.parameter))
		if parameter is not None:
			c.parseParameter(parameter)

		return c

	def _parseParameterDefault(self, encoded):
		parameter = Encoding.StringToNumber(encoded)
		if self.getName() not in (
			Command.NAME.MY,
			Command.NAME.__getattribute__('%V'),
		):
			log.warning(('uncertain conversion of encoded parameter'
				+ ' "%s" to number 0x%X for command %s')
				% (encoded, parameter, self.getName()))
		return parameter

	def parseParameter(self, encoded):
		n = self.getName()
		if n is Command.NAME.ND:
			parameter = Protocol.ParseNodeDiscover(encoded)
		else:
			parameter = self._parseParameterDefault(encoded)
		self.setParameter(parameter)

