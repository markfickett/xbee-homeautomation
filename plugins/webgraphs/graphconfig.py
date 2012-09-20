graphs = []
# Graph names should be lowercase letters only, to be used in css identifiers.


def _voltsToC(volts):
	"""
	Convert numeric volts to numeric degrees centigrade, for a TMP36.
	"""
        return volts * 100 - 50


def _voltsToF(volts):
	"""
	Convert numeric volts to numeric degrees Fahrenheit.
	"""
        return _voltsToC(volts) * (9.0/5.0) + 32


def voltsToF(voltsStr):
	"""
	Convert a string-formatted volts value to a string-formatted
	temperature (degrees Fahrenheit).
	"""
        return str(_voltsToF(float(voltsStr)))


graphs.append(('temperature', {
	'title': 'Temperature (deg F)',
	'map': voltsToF,
	'series': {
		'0x0013a200408cca0e-AD0': [
			{	'title': 'Bathroom',
			},
		],
		'0x0013a200408cca0e-AD1': [
			{	'title': 'Outside',
				'lastDate': '2012 Sep 12 03:44:30 UTC',
			},
			{	'title': 'Living Room (on wires)',
			},
		],
		'0x0013a200408cca0e-AD2': [
			{	'title': 'Bathroom',
				'lastDate': '2012 Sep 12 03:44:30 UTC',
			},
			{	'title': 'Living Room (on board)',
			},
		],
		'0x0013a200409028b6-AD0': [
			{	'title': 'Bedroom',
			},
		],
	},
	'annotations': [
		{	'series': 'Bathroom',
			'x': '2012 Aug 27 22:54:44 UTC',
			'shortText': 'X',
			'text': 'no reverse-voltage protection (sensor fried)',
		},
		{	'series': 'Bedroom',
			'x': '2012 Aug 28 04:20:51 UTC',
			'shortText': 'AC',
			'text': 'turn on air conditioning (central air)',
		},
		{	'series': 'Outdoor',
			'x': '2012 Aug 28 14:26:02 UTC',
			'shortText': 'Rn',
			'text': 'rain ends mid-morning',
		},
		{	'series': 'Bedroom',
			'x': '2012 Sep 03 15:53:04 UTC',
			'shortText': 'Gn',
			'text': 'gone with computer for the day',
		},
		{	'series': 'Bedroom',
			'x': '2012 Sep 05 06:42:18 UTC',
			'shortText': 'Sl',
			'text': 'computer went to sleep',
		},
		{	'series': 'Outdoor',
			'x': '2012 Sep 05 17:01:09 UTC',
			'shortText': '?',
			'text': 'intermittent rejoining / not sending IO'
				+ ' samples',
		},
		{	'series': 'Bedroom',
			'x': '2012 Sep 06 01:36:24 UTC',
			'shortText': 'SN',
			'text': 'shortened number of sleep periods'
				+ ' from 10 to 5',
		},
		{	'series': 'Bathroom',
			'x': '2012 Sep 09 00:44:28 UTC',
			'shortText': 'X',
			'text': 'bogus -58F recorded for bathroom/outdoor:'
				+ ' removed',
		},
		{	'series': 'Bedroom',
			'x': '2012 Sep 12 03:01:42 UTC',
			'shortText': 'S',
			'text': 'moved coordinator XBee to server machine',
		},
		{	'series': 'Bathroom',
			'x': '2012 Sep 12 03:34:44 UTC',
			'shortText': 'B',
			'text': 'new board for bathroom/outdoor XBee:'
				+ ' seats properly',
		},
		{	'series': 'Living Room (on board)',
			'x': '2012 Sep 13 03:32:39 UTC',
			'shortText': 'Lr',
			'text': 'move outdoor/bathroom XBee to living room:'
				+ ' closer to coordinator XBee',
		},
		{	'series': 'Living Room (on board)',
			'x': '2012 Sep 13 17:37:15 UTC',
			'shortText': 'Su',
			'text': 'guess: sun through the window on the sensor',
		},
		{	'series': 'Bedroom',
			'x': '2012 Sep 14 00:00:01 UTC',
			'shortText': 'F',
			'text': 'start evacuative window fan in LR'
				+ ' with BR window open',
		},
		{	'series': 'Bedroom',
			'x': '2012 Sep 14 02:45:20 UTC',
			'shortText': 'F',
			'text': 'evacuative window fan on',
		},
		{	'series': 'Living Room (on board)',
			'x': '2012 Sep 19 21:35:23 UTC',
			'shortText': 'D',
			'text': 'leave door open',
		},
	],
}))

graphs.append(('voltage', {
	'title': 'Voltage',
	'series': {
		'0x0013a200408cca0e-VCC': [
			{	'title': 'NiMH',
				'lastDate': '2012 Aug 27 08:08:19 UTC',
			},
			{	'title': 'LiPo',
				'lastDate': '2012 Aug 27 12:54:39 UTC',
			},
			{	'title': 'FTDI Adapter',
				'lastDate': '2012 Aug 28 00:54:24 UTC',
			},
			{	'title': 'LiPo',
				'lastDate': '2012 Aug 29 09:36:44 UTC',
			},
			{	'title': 'NiMH',
				'lastDate': '2012 Aug 31 04:26:45 UTC',
			},
			{	'title': 'LiPo',
			},
		],
		'0x0013a200409028b6-VCC': [
			{	'title': 'LiPo',
				'lastDate': '2012 Aug 27 08:03:18 UTC',
			},
			{	'title': 'NiMH',
				'lastDate': '2012 Aug 27 12:57:58 UTC',
			},
			{	'title': 'LiPo',
				'lastDate': '2012 Aug 28 00:54:24 UTC',
			},
			{	'title': 'FTDI Adapter',
				'lastDate': '2012 Sep 03 13:23:18 UTC',
			},
			{	'title': 'NiMH',
			},
		],
		'0x0013a200409029bd-VCC': [{'title': 'USB'}],
	},
	'annotations': [
		{	'series': 'FTDI Adapter',
			'x': '2012 Aug 28 01:01:34 UTC',
			'shortText': '3v',
			'text': '3.3v regulated from FTDI USB adapter'
				+ ' attached to A/C adapter',
		},
		{	'series': 'NiMH',
			'x': '2012 Aug 29 10:51:44 UTC',
			'shortText': 'A',
			'text': 'fresh 3xNiMH charge, no sleeping',
		},
		{	'series': 'LiPo',
			'x': '2012 Aug 31 12:08:14 UTC',
			'shortText': 'A',
			'text': 'fresh LiPo charge, no sleeping',
		},
		{	'series': 'LiPo',
			'x': '2012 Sep 03 02:36:12 UTC',
			'shortText': 'S',
			'text': 'fresh LiPo charge, with 28s sleep cycle'
				+ ' and 5 minute sampling cycle',
		},
		{	'series': 'NiMH',
			'x': '2012 Sep 03 13:35:09 UTC',
			'shortText': 'S',
			'text': 'fresh 3xNiMH charge, with 28s sleep cycle'
				+ ' and 5 minute sampling cycle',
		},
	],
}))

