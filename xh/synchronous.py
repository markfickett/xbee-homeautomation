"""
Functions for synchronously sending Commands and waiting for responses.
"""

import logging
import multiprocessing
import time

from . import signals


__all__ = [
	'SendAndWait',
	'SendAndAccumulate',
]


log = logging.getLogger('synchronous')

TIMEOUT_SECONDS = 0.2
CHECK_INTERVAL_SECONDS = 0.01
TimeoutError = multiprocessing.TimeoutError



class _Response:
	def __init__(self):
		self.__value = None


	def get(self):
		return self.__value


	def set(self, v):
		self.__value = v



def SendAndWait(command, xb=None):
	"""
	Send a Command and wait for its (single) response.
	@return the Frame received in response
	@raise TimeoutError if no response is received
		within a short timeout
	"""
	r = _Response()
	id = command.getFrameId()
	def recordSingleResponseCb(sender=None, signal=None, frame=None):
		if hasattr(frame, 'getFrameId') and frame.getFrameId() == id:
			r.set(frame)
	signals.FRAME_RECEIVED.connect(recordSingleResponseCb)
	command.send(xb=xb)

	elapsed = 0
	while r.get() is None and elapsed <= TIMEOUT_SECONDS:
		time.sleep(CHECK_INTERVAL_SECONDS)
		elapsed += CHECK_INTERVAL_SECONDS
	signals.FRAME_RECEIVED.disconnect(recordSingleResponseCb)
	if r.get() is None:
		raise TimeoutError('No response after %.3fs waiting for %s'
			% (TIMEOUT_SECONDS, command))
	else:
		return r.get()


def SendAndAccumulate(command, timeoutSeconds, xb=None):
	"""
	Send a Command and wait to accumulate multiple responses.
	@return a list of Frames received in response
	"""
	r = _Response()
	r.set([])

	id = command.getFrameId()
	def accumulateMultipleCallback(sender=None, signal=None, frame=None):
		if hasattr(frame, 'getFrameId') and frame.getFrameId() == id:
			r.get().append(frame)
	signals.FRAME_RECEIVED.connect(accumulateMultipleCallback)
	command.send(xb=xb)
	time.sleep(timeoutSeconds)
	signals.FRAME_RECEIVED.disconnect(accumulateMultipleCallback)

	return r.get()

