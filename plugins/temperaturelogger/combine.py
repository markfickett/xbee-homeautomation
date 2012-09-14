"""
Generate a combined CSV for graphing via dygraph.

Temperature values are from a TEMP36
(see http://learn.adafruit.com/tmp36-temperature-sensor ).
"""

import datetime
import logging
import os
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import xh

log = logging.getLogger('combine')
log.setLevel(logging.WARNING)

DATA_DIR = xh.Config.DATA_DIR
def getUploadTarget():
	name = 'DATA_UPLOAD_TARGET'
	return getattr(xh.Config, name) if hasattr(xh.Config, name) else None
DATA_UPLOAD_TARGET = getUploadTarget()

OUT_FILE_NAME_TEMPLATE = os.path.join(DATA_DIR, 'combined-%s.csv')
TIMESTAMP_COLUMN_HEADER = 'Timestamp'
DATETIME_FORMAT = xh.datalogging.DATETIME_FORMAT
# See Dygraph.dateParser:
# https://github.com/danvk/dygraphs/blob/master/dygraph-utils.js#L517
DYGRAPH_FORMAT = '%Y-%m-%d %H:%M:%S UTC'
GAP_DT = datetime.timedelta(minutes=10)
GAP_VALUE = 'NaN'


TEMPERATURE_NAMES = {
	'datalog-0x0013a200408cca0e-AD0.csv': 'Bathroom a',
	'datalog-0x0013a200408cca0e-AD1.csv': 'Outdoor',
	# use AD2 to take over but not connect to old line
	'datalog-0x0013a200408cca0e-AD2.csv': 'Bathroom b',
	'datalog-0x0013a200409028b6-AD0.csv': 'Bedroom',


	'datalog-0x0013a200408cca0e-AD3.csv': '0e AD3',
	'datalog-0x0013a200409028b6-AD1.csv': 'b6 AD1',
	'datalog-0x0013a200409028b6-AD2.csv': 'b6 AD2',
	'datalog-0x0013a200409028b6-AD3.csv': 'b6 AD3',
}
OUT_TEMPERATURE_FILE_NAME = OUT_FILE_NAME_TEMPLATE % 'temperature'


VOLTAGE_NAMES = {
	'datalog-0x0013a200409028b6-VCC.csv': 'Bedroom',
	'datalog-0x0013a200408cca0e-VCC.csv': 'Bathroom',
}
OUT_VOLTAGE_FILE_NAME = OUT_FILE_NAME_TEMPLATE % 'voltage'


def addRow(combinedMap, nColumns, d, columnIndex, valueStr):
	row = combinedMap.get(d)
	if row is None:
		row = ['',]*nColumns
		combinedMap[d] = row
	row[columnIndex] = valueStr


def writeCombinedCsv(outFileName, inNameMap, mapFn=None):
	combinedMap = {}
	columnNames = inNameMap.values()
	nColumns = len(columnNames)
	for inFileLocalName, columnName in inNameMap.iteritems():
		inFileName = os.path.join(DATA_DIR, inFileLocalName)
		log.debug('Processing %s' % inFileName)
		if not os.path.isfile(inFileName):
			log.info('Not a file, skipping: %s' % inFileName)
			continue
		columnIndex = columnNames.index(columnName)
		with open(inFileName) as inFile:
			lastD = None
			for rowStr in inFile:
				dateStr, valueStr = rowStr.strip().split(',')
				d = datetime.datetime.strptime(dateStr,
					DATETIME_FORMAT)
				if lastD is not None and (d - lastD) > GAP_DT:
					addRow(combinedMap, nColumns, d-GAP_DT,
							columnIndex, GAP_VALUE)
				if mapFn:
					valueStr = mapFn(valueStr)
				addRow(combinedMap, nColumns, d,
						columnIndex, valueStr)
				lastD = d
	headers = [TIMESTAMP_COLUMN_HEADER,] + columnNames
	combinedRows = [[d.strftime(DYGRAPH_FORMAT),] + rowValues for
		d, rowValues in sorted(combinedMap.items())]
	combinedRows.insert(0, headers)

	with open(outFileName, 'w') as outFile:
		for row in combinedRows:
			outFile.write(','.join(row) + '\n')


def _voltsToC(volts):
	return volts * 100 - 50

def _voltsToF(volts):
	return _voltsToC(volts) * (9.0/5.0) + 32

def voltsToF(voltsStr):
	return str(_voltsToF(float(voltsStr)))


writeCombinedCsv(OUT_TEMPERATURE_FILE_NAME, TEMPERATURE_NAMES, mapFn=voltsToF)
writeCombinedCsv(OUT_VOLTAGE_FILE_NAME, VOLTAGE_NAMES)

if DATA_UPLOAD_TARGET:
	uploadCommand = [
		'rsync',
		'-rv',
		DATA_DIR + os.path.sep,
		DATA_UPLOAD_TARGET,
		'--include=combined-*',
		'--exclude=*',
	]
	log.debug('running %s' % uploadCommand)
	result = subprocess.call(uploadCommand)
	log.info('%s exited with status %d' % (uploadCommand[0], result))
else:
	log.warning('No xh.Config.DATA_UPLOAD_TARGET found (expected to be in'
			+ ' SecretConfig), skipping upload.')

