NAMES = {
	'datalog-0x13a200408cca0e-AD0-F.csv':
			'datalog-0x13a200408cca0e-AD0.csv',
	'datalog-0x13a200408cca0e-AD2-F.csv':
			'datalog-0x13a200408cca0e-AD2.csv',
	'datalog-0x13a200408cca0e-AD1-F.csv':
			'datalog-0x13a200408cca0e-AD1.csv',
	'datalog-0x13a200409028b6-AD0-F.csv':
			'datalog-0x13a200409028b6-AD0.csv',
}

def _fahToV(fah):
	return ((fah - 32) * (5.0/9.0) + 50) / 100.0

def fahToV(fahStr):
	return str(_fahToV(float(fahStr)))

for fahFileName, voltsFileName in NAMES.iteritems():
	with open(fahFileName) as fahFile:
		with open(voltsFileName, 'w') as voltsFile:
			for line in fahFile:
				t, v = line.strip().split(',')
				v = fahToV(v)
				voltsFile.write('%s,%s\n' % (t, v))

