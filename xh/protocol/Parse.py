import logging
log = logging.getLogger('ParsedFromDict')

from .. import Encoding, EnumUtil
from . import Command, CommandRegistry, Data, Frame


def ParseFromDict(d):
	"""
	Parse common fields from a response dict and create a Frame of the
	appropriate class.
	"""
	usedKeys = set()

	frameTypeKey = str(Frame.FIELD.id)
	frameType = EnumUtil.FromString(Frame.TYPE, d[frameTypeKey])
	usedKeys.add(frameTypeKey)

	if frameType is Frame.TYPE.at_response:
		o = _ParseAtCommand(d, usedKeys)
	elif frameType is Frame.TYPE.rx_io_data_long_addr:
		o = _ParseData(d, usedKeys)

	unusedKeys = set(d.keys()).difference(usedKeys)
	if unusedKeys:
		unused = {}
		for k in unusedKeys:
			unused[k] = d[k]
		log.warning('In parsing %s, did not use %s.' % (o, unused))

	return o


def _ParseAtCommand(d, usedKeys):
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
		c = commandClass(frameId=frameId)
	else:
		c = Command(name, frameId=frameId)
	usedKeys.update(c.mergeFromDict(d))

	return c


def _ParseData(d, usedKeys):
	parsedData = Data()
	usedKeys.update(parsedData.mergeFromDict(d))
	return parsedData

