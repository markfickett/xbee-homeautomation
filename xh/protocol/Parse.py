import logging
log = logging.getLogger('ParsedFromDict')

from .. import Encoding, EnumUtil
from . import Command, CommandRegistry, Data, Frame, FrameRegistry, NodeId


def ParseFromDict(d):
	"""
	Parse common fields from a response dict and create a Frame of the
	appropriate class.
	"""
	usedKeys = set()

	frameTypeKey = str(Frame.FIELD.id)
	frameType = EnumUtil.FromString(Frame.TYPE, d[frameTypeKey])
	usedKeys.add(frameTypeKey)

	frameClass = FrameRegistry.get(frameType)
	if frameClass is None:
		raise RuntimeError(('No Frame subclass to handle parsing '
			+ 'Frame.TYPE.%s. Data to parse: %s') % (frameType, d))

	frame = frameClass.CreateFromDict(d, usedKeys)

	unusedKeys = set(d.keys()).difference(usedKeys)
	if unusedKeys:
		unused = {}
		for k in unusedKeys:
			unused[k] = d[k]
		log.warning('In parsing %s, did not use %s.' % (frame, unused))

	return frame


