import datetime
import json
import logging

import xh


log = logging.getLogger('webgraphs.combine')
TIMESTAMP_COLUMN_HEADER = 'Timestamp'
GAP_VALUE = 'datagap'
GAP_DT = datetime.timedelta(minutes=10)
EPOCH = datetime.datetime.utcfromtimestamp(0)


def _addToRow(rowDataMap, timestamp, value, columnIndex, numColumns):
	row = rowDataMap.get(timestamp)
	if row is None:
		row = [None]*numColumns
		rowDataMap[timestamp] = row
	row[columnIndex] = value


def _getEpochMillis(d):
	delta = d - EPOCH
	return delta.total_seconds() * 1000


def _getJsDateString(d):
	return 'new Date(%d)' % _getEpochMillis(d)


def buildJsData(graphDefinitions, allLogData):
	"""
	Use graph definitions to transform log data into javascript blobs
	appropriate for Dygraph.
	"""
	seriesDefinitions = graphDefinitions['series']

	# build a dict of {name for output: {date object: numeric value}}
	# insert gap markers
	allSeriesData = {}
	for logName, optionsList in seriesDefinitions.iteritems():
		if len(optionsList) != 1:
			raise RuntimeError('for now expect all to have one')
		optionsDict = optionsList[0]
		logData = allLogData.get(logName)
		if not logData:
			log.warning('no data for %s, series are %s',
					logName, allLogData.keys())
			continue
		seriesTitle = optionsDict.get('title', logName)
		mapFn = optionsDict['map']
		seriesData = allSeriesData.get(seriesTitle)
		if seriesData is None:
			seriesData = {}
			allSeriesData[seriesTitle] = seriesData
		lastD = None
		for d, valueStr in logData:
			seriesData[d] = mapFn(valueStr)
			if lastD is not None and (d - lastD) > GAP_DT:
				seriesData[lastD+GAP_DT] = GAP_VALUE
			lastD = d

	seriesTitles = allSeriesData.keys()
	numSeries = len(seriesTitles)
	# build a combined dict of {date object: (row entries)}
	rowData = {}
	for seriesName, seriesValuesDict in allSeriesData.iteritems():
		seriesIndex = seriesTitles.index(seriesName)
		for d, v in seriesValuesDict.iteritems():
			_addToRow(rowData, d, v, seriesIndex, numSeries)

	# build javascript text
	dataJsStr = '[\n'
	for d, rowValues in sorted(rowData.items()):
		rowValuesJs = []
		dataJsStr += '\t['
		rowValuesJs.append(_getJsDateString(d))
		for v in rowValues:
			if v is GAP_VALUE:
				rowValuesJs.append('NaN')
			elif v is None:
				rowValuesJs.append('null')
			else: # must be numeric
				rowValuesJs.append(str(v))
		dataJsStr += ','.join(rowValuesJs)
		dataJsStr += '],\n'
	dataJsStr += '\n]'

	labels = [TIMESTAMP_COLUMN_HEADER,] + seriesTitles
	labelsJsStr = json.dumps(labels)

	annotationsParsed = []
	for annotationDict in graphDefinitions['annotations'] or []:
		d = dict(annotationDict)
		d['x'] = _getEpochMillis(xh.datalogging.parseTimestamp(d['x']))
		annotationsParsed.append(d)
	annotationJsStr = json.dumps(annotationsParsed)
	
	return labelsJsStr, dataJsStr, annotationJsStr


