import logging

from .deps import pysignals

log = logging.getLogger('signals')


def _isErrorTuple(o):
	"""
	@return whether the given object looks like an error tuple, as from
		sys.exc_info().
	"""
        return (isinstance(o, tuple)
                and len(o) == 3
                and type(o[0]) == type)


def logErrors(responses):
	"""
	@param responses a list of responses or errors as from send_robust
	"""
	for receiver, responseOrErr in responses:
		if not _isErrorTuple(responseOrErr):
			continue
		formatted = ''.join(traceback.
		format_exception(*responseOrErr))
		log.error(('error in receiver %s handling %s:\n%s')
				% (receiver, frame, rawData, formatted))


# sent when any frame is received by the local XBee
FRAME_RECEIVED = pysignals.Signal(providing_args=['frame'])

# Sent when any data is logged using xh.datalogging. The args serial and
# pinName are sent if the value was logged as a pin value (as opposed to a
# generic named value).
DATA_LOGGED = pysignals.Signal(providing_args=[
	'name',
	'value',
	'formattedValue',
	'timestamp',
	'formattedTimestamp',
	'serial',
	'pinName',
])
