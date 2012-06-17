import logging
log = logging.getLogger('ParseCommandFromDict')

from .. import Encoding, EnumUtil
from . import Command, InputVolts, NodeDiscover


# map from Command.NAME to the associated class
COMMAND_CLASSES = {
	Command.NAME.__getattribute__('%V'): InputVolts,
	Command.NAME.ND: NodeDiscover,
}


def ParseCommandFromDict(d):
	"""
	Parse common fields from a response dict and create a Command of the
	appropriate class.
	"""
	usedKeys = set()
	frameIdKey = str(Command.FIELD.frame_id)
	frameId = Encoding.PrintedStringToNumber(d[frameIdKey])
	usedKeys.add(frameIdKey)

	nameKey = str(Command.FIELD.command)
	name = EnumUtil.FromString(Command.NAME, d[nameKey])
	usedKeys.add(nameKey)

	commandClass = COMMAND_CLASSES.get(name)
	if commandClass:
		c = commandClass(frameId=frameId)
	else:
		c = Command(name, frameId=frameId)
	usedKeys.update(c.mergeFromDict(d))

	unusedKeys = set(d.keys()).difference(usedKeys)
	if unusedKeys:
		unused = {}
		for k in unusedKeys:
			unused[k] = d[k]
		log.warning('In parsing %s, did not use %s.' % (c, unused))

	return c

