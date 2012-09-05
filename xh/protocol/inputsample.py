import logging

from .. import encoding
from . import AnalogSample, Command, CommandRegistry, DigitalSample

log = logging.getLogger('InputSample')



class InputSample(Command):
	"""
	Force samples to be taken of all the configured input pins. The samples
	are sent in the IS response frame. A module with no pins configured as
	input will respond with an error.

	Note that sleeping devices will not wait before sampling upon receipt of
	this command (see also NumberOfSleepPeriods and WakeHostTimer).
	"""
	_EXPECTED_NUM_SETS = 1


	def __init__(self, **kwargs):
		Command.__init__(self, Command.NAME.IS, **kwargs)
		self.__samples = None


	def getSamples(self):
		return self.__samples and list(self.__samples)


	def parseParameter(self, encoded):
		"""
		Parse the Command's response parameter into samples. The
		expected format is like the IO Data Sample Rx Indicator frame
		(see page 114 of the Xbee series 2 datasheet for the I/O frame
		overview, and page 96 for the sample parameter details):
			offset	description
			0	receive options: 0x01 = ack, 0x02 = broadcast
			1-2	digital channel mask (bit field)
			3	analog channel mask
			?4-5	digital samples (bit field, matching channels,
				only present if any digital channels are on)
			6-7+	optional analog samples (two bytes each)
		"""
		self.setParameter(encoded)
		self.__samples = []
		offset = 0

		# The number of sample sets is expected to always be 1.
		numSets = encoding.StringToNumber(encoded[offset:offset+1])
		if numSets != self._EXPECTED_NUM_SETS:
			raise RuntimeError(('Number of sample sets is expected '
			+ 'to always be %d, but is %d.')
			% (self._EXPECTED_NUM_SETS, numSets))
		offset += 1

		digitalPinNumbers = encoding.BitFieldToIndexSet(
			encoding.StringToNumber(encoded[offset:offset+2]))
		offset += 2

		analogPinNumbers = sorted(encoding.BitFieldToIndexSet(
			encoding.StringToNumber(encoded[offset:offset+1])))
		offset += 1

		if digitalPinNumbers:
			digitalOnValues = encoding.BitFieldToIndexSet(
				encoding.StringToNumber(
					encoded[offset:offset+2]))
			offset += 2
		else:
			digitalOnValues = set()

		analogValues = []
		while offset + 2 <= len(encoded):
			analogValues.append(encoding.StringToNumber(
				encoded[offset:offset+2]))
			offset += 2

		for digitalPinNum in digitalPinNumbers:
			digitalValue = digitalPinNum in digitalOnValues
			self.__samples.append(DigitalSample.CreateFromRawValues(
				digitalPinNum, digitalValue))

		for analogPinNum, analogValueNum in zip(
				analogPinNumbers, analogValues):
			analogSample = AnalogSample.CreateFromRawValues(
				analogPinNum, analogValueNum)
			self.__samples.append(analogSample)


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		d.update({'samples': self.getSamples()})
		return d



CommandRegistry.put(Command.NAME.IS, InputSample)
