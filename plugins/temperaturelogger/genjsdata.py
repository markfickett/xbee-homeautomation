"""
Generate the javascript data for graphs.
"""

import os

from locations import DATA_DIR


# Limit to entries timestamped after a certain time. (Evaluated by
# simple string prefix matching, so avoid seconds and maybe minutes.)
LIMIT_TO_TIMES_AFTER = None
#LIMIT_TO_TIMES_AFTER = '2012 Aug 28 04:'
#LIMIT_TO_TIMES_AFTER = '2012 Aug 29 03:' # 11p Tuesday Aug 28
#LIMIT_TO_TIMES_AFTER = '2012 Aug 29 08:'

JS_OUT_FILE_NAME = 'graphdata.js'

TEMPERATURE_NAMES = {
	'datalog-0x13a200408cca0e-AD0-F.csv': 'Bathroom a',
	'datalog-0x13a200408cca0e-AD1-F.csv': 'Outdoor',
	# use AD2 to take over but not connect to old line
	'datalog-0x13a200408cca0e-AD2-F.csv': 'Bathroom b',
	'datalog-0x13a200409028b6-AD0-F.csv': 'Bedroom',


	'datalog-0x13a200408cca0e-AD3-F.csv': '0e AD3',
	'datalog-0x13a200409028b6-AD1-F.csv': 'b6 AD1',
	'datalog-0x13a200409028b6-AD2-F.csv': 'b6 AD2',
	'datalog-0x13a200409028b6-AD3-F.csv': 'b6 AD3',
}
TEMPERATURE_VAR_NAME = 'loggedTemperatureData'

VOLTAGE_NAMES = {
	'datalog-0x13a200409028b6-VCC.csv': 'Bedroom',
	'datalog-0x13a200408cca0e-VCC.csv': 'Bathroom',
}
VOLTAGE_VAR_NAME = 'loggedVoltageData'


def writeJsDataLines(jsOutFile, dataFile):
	outLines = []
	writeLine = LIMIT_TO_TIMES_AFTER is None
	for line in dataFile:
		timestampStr, valueStr = line.strip().split(',')
		if not writeLine:
			writeLine = timestampStr.startswith(
				LIMIT_TO_TIMES_AFTER)
			continue
		jsOutFile.write("\t['%s', %s],\n" % (timestampStr, valueStr))
				
def writeJsData(jsOutFile, dataVarName, dataFilesToNames):
	jsOutFile.write('var %s = [];\n\n' % dataVarName);
	for dataFileLocalName, dataName in dataFilesToNames.iteritems():
		dataFileName = os.path.join(DATA_DIR, dataFileLocalName)
		if not os.path.isfile(dataFileName):
			continue
		jsOutFile.write("%s.push(['%s', [\n" % (dataVarName, dataName));
		with open(dataFileName) as dataFile:
			writeJsDataLines(jsOutFile, dataFile)
		jsOutFile.write("]]);\n\n");

with open(JS_OUT_FILE_NAME, 'w') as jsOutFile:
	writeJsData(jsOutFile, TEMPERATURE_VAR_NAME, TEMPERATURE_NAMES)
	writeJsData(jsOutFile, VOLTAGE_VAR_NAME, VOLTAGE_NAMES)

