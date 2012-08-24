import logging
import xh

log = logging.getLogger('FrameLogger')



class FrameLogger(xh.Plugin):
	"""
	Log all received Frames using the logging library (at INFO level),
	and make a history of received Frames available.
	"""
	FRAME_HISTORY_LIMIT = 700
	FRAME_HISTORY_TRIM = 500


	def __init__(self):
		xh.Plugin.__init__(self, receiveFrames=True)
		self.__frameHistory = []


	def _frameReceived(self, frame):
		log.info('received %s' % frame)

		self.__frameHistory.insert(0, frame)
		if len(self.__frameHistory) > self.FRAME_HISTORY_LIMIT:
			self.__frameHistory = self.__frameHistory[
				:self.FRAME_HISTORY_TRIM]


	def getLatestFrame(self):
		"""
		@return the latest Frame received, or None
		"""
		return (self.__frameHistory[0] if len(self.__frameHistory) > 0
			else None)


	def getFrame(self, i):
		"""
		@return the ith oldest Frame received
		"""
		return self.__frameHistory[i]


	def getFrameHistory(self):
		"""
		@return a copy of the current Frame history, with the most
			recent Frame (if any) at index 0
		"""
		return list(self.__frameHistory)

