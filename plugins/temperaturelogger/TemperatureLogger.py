import xh
import datetime, threading, logging
from xh.protocol import PIN

log = logging.getLogger('TemperatureLogger')



class TemperatureLogger(xh.Plugin):
	_INPUT_VOLTS_QUERY_INTERVAL_SEC = 5 * 60.0


	def __init__(self):
		xh.Plugin.__init__(self, receiveFrames=True)


	def activate(self):
		xh.Plugin.activate(self)
		serials = self.getSerials()
		if serials:
			self.__sendInputVoltsQueryAndRepeat(serials)
		else:
			log.warning(('%s has no associated serials, will not '
			+ 'query for input voltage levels.')
			% self.__class__.__name__)


	def __sendInputVoltsQueryAndRepeat(self, serials):
		thread = threading.Timer(self._INPUT_VOLTS_QUERY_INTERVAL_SEC,
			self.__sendInputVoltsQueryAndRepeat, args=[serials,])
		thread.daemon = True
		thread.start()
		for s in serials:
			xh.protocol.InputVolts(dest=s).send()


	def _frameReceived(self, frame):
		serials = self.getSerials()
		if isinstance(frame, xh.protocol.Data):
			sourceSerial = frame.getSourceAddressLong()
			if sourceSerial not in serials:
				return
			t = frame.getTimestamp()
			for sample in frame.getSamples():
				self.__logSample(sourceSerial, t, sample)
		elif isinstance(frame, xh.protocol.InputVolts):
			sourceSerial = frame.getRemoteSerial()
			if sourceSerial not in serials:
				return
			self.__recordValue(sourceSerial,
				datetime.datetime.utcnow(),
				'Vcc',
				frame.getVolts())
		elif isinstance(frame, xh.protocol.InputSample):
			sourceSerial = frame.getRemoteSerial()
			if sourceSerial not in serials:
				return
			t = datetime.datetime.utcnow()
			for sample in frame.getSamples():
				self.__logSample(sourceSerial, t, sample)


	@staticmethod
	def __voltsToF(volts):
		return ((volts*100 - 50) * (9.0/5.0) + 32)


	@staticmethod
	def __voltsToPercentOfMax(volts):
		return (volts/1.06) * 100


	def __logSample(self, sourceSerial, timestamp, sample):
		p = sample.getPinName()
		if p is PIN.AD0:
			name = 'Fahrenheit'
			value = self.__voltsToF(sample.getVolts())
		elif p is PIN.AD1:
			name = 'Light'
			value = self.__voltsToPercentOfMax(sample.getVolts())
		else:
			raise RuntimeError(
				('%s plugin not configured to handle pin %s '
					+ 'from module 0x%x.'),
				(self.__class__.__name__,
					p, sourceSerial))
		self.__recordValue(sourceSerial, timestamp, name, value)


	def __recordValue(self, sourceSerial, timestamp, textName, value):
		name = '0x%x %s' % (sourceSerial, textName)
		log.debug('%s\t%s\t%.3f'
			% (xh.protocol.Data.FormatTimestamp(timestamp),
				name, value))


