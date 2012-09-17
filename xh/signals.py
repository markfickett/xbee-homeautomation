from .deps import pysignals

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
