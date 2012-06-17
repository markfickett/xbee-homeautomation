import logging
log = logging.getLogger('ParseCommandFromDict')

from .. import Encoding, EnumUtil
from . import Command, CommandRegistry


def ParseCommandFromDict(d):
	"""
	Parse common fields from a response dict and create a Command of the
	appropriate class.
	"""
	usedKeys = set()
	frameIdKey = str(Command.FIELD.frame_id)
	frameId = Encoding.PrintedStringToNumber(d[frameIdKey])
	usedKeys.add(frameIdKey)

	frameTypeKey = str(Command.FIELD.id)
	frameType = EnumUtil.FromString(Command.FRAME_TYPE, d[frameTypeKey])
	usedKeys.add(frameTypeKey)

	nameKey = str(Command.FIELD.command)
	name = EnumUtil.FromString(Command.NAME, d[nameKey])
	usedKeys.add(nameKey)

	commandClass = CommandRegistry.get(name)
	if commandClass:
		c = commandClass(frameId=frameId, frameType=frameType)
	else:
		c = Command(name, frameId=frameId, frameType=frameType)
	usedKeys.update(c.mergeFromDict(d))

	unusedKeys = set(d.keys()).difference(usedKeys)
	if unusedKeys:
		unused = {}
		for k in unusedKeys:
			unused[k] = d[k]
		log.warning('In parsing %s, did not use %s.' % (c, unused))

	return c

