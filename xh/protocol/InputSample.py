from .. import Encoding
from . import AnalogSample, Command, CommandRegistry, DigitalSample



class InputSample(Command):
	"""
	Force samples to be taken of all the configured input pins. The samples
	are sent in the IS response frame. A module with no pins configured as
	input will respond with an error.
	"""


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
			4-5	digital samples (bit field, matching channels)
			6-7+	optional analog samples (two bytes each)
		"""
		self.setParameter(encoded)
		self.__samples = []
		offset = 0

		self._parseOptions(encoded[offset:offset+1])
		offset += 1

		digitalPinNumbers = Encoding.BitFieldToIndexSet(
			encoded[offset:offset+2])
		offset += 2

		analogPinNumbers = sorted(Encoding.BitFieldToIndexSet(
			encoded[offset:offset+1]))
		offset += 1

		digitalOnValues = Encoding.BitFieldToIndexSet(
			encoded[offset:offset+2])

		analogValues = []
		while offset + 1 < len(encoded):
			analogValues.append(Encoding.StringToNumber(
				encoded[offset:offset+1]))
			offset += 1

		for digitalPinNum in digitalPinNumbers:
			digitalValue = digitalPinNum in digitalOnValues
			self.__samples.append(DigitalSample.CreateFromRawValues(
				digitalPinNum, digitalValue))

		for analogPinNum, analogValueNum in zip(
		analogPinNumbers, analogValues):
			self.__samples.append(AnalogSample.CreateFromRawValues(
				analogPinNum, analogValueNum))


	def getNamedValues(self):
		d = Command.getNamedValues(self, includeParameter=False)
		d.update({'samples': self.getSamples()})
		return d



CommandRegistry.put(Command.NAME.IS, InputSample)
