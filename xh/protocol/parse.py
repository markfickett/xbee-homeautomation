import logging

from .. import encoding, enumutil
from . import Command, CommandRegistry, Data, Frame, FrameRegistry, NodeId


log = logging.getLogger('ParsedFromDict')


def ParseFromDictSafe(d):
	"""
	Call ParseFromDict to create a Frame from an API response dict,
	converting any errors to logged errors.
	@return a Frame (subclass) on successful parsing or None on error
	"""
	try:
		return ParseFromDict(d)
	except:
		log.error('error handling data: %s' % d, exc_info=True)
		return None


def ParseFromDict(d):
	"""
	Parse common fields from a response dict and create a Frame of the
	appropriate class.
	"""
	usedKeys = set()

	frameTypeKey = str(Frame.FIELD.id)
	frameType = enumutil.fromString(Frame.TYPE, d[frameTypeKey])
	usedKeys.add(frameTypeKey)

	frameClass = FrameRegistry.get(frameType)
	if frameClass is None:
		raise RuntimeError(('No Frame subclass to handle parsing '
			+ 'Frame.TYPE.%s. Data to parse: %s') % (frameType, d))

	frame = frameClass.createFromDict(d, usedKeys)

	unusedKeys = set(d.keys()).difference(usedKeys)
	if unusedKeys:
		unused = {}
		for k in unusedKeys:
			unused[k] = d[k]
		log.warning('In parsing %s, did not use %s.' % (frame, unused))

	return frame


