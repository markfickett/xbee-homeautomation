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


def _buildSeriesData(seriesDefinitions, allLogData, mapFn):
	"""
	Convert from log data, named by data source, of the form:
		{ loggedName: [ datetime: rawValueStr, ... ], ...  }
	to series data, with semantic names and mapped values, of the form:
		{ seriesName: { datetime: mappedValueStr, ... }, ... }
	Also insert gap markers (GAP_VALUE) where no data was logged for GAP_DT.
	"""
	allSeriesData = {}
	for logName, optionsList in seriesDefinitions.iteritems():
		logData = allLogData.get(logName)
		if not logData:
			log.warning('no data for %s, series are %s',
					logName, logData.keys())
			continue

		dataStartIndex = 0
		for optionsDict in optionsList:
			dataStartIndex = _addToSeriesData(allSeriesData,
					optionsDict, logName, logData,
					mapFn, dataStartIndex)

		n = len(logData)
		if dataStartIndex < n:
			log.warning('only used %d of %d entries for %s.',
					dataStartIndex, n, logName)

	return allSeriesData


def _addToSeriesData(allSeriesData, optionsDict, logName, logData,
		mapFn, startDataIndex):
	"""
	Update the series data dict with data from one log-data source according
	to one series definition.

	If optionsDict contains 'lastDate', do not process any logged data
	dated later than lastDate.
	"""
	n = len(logData)
	if not startDataIndex < n:
		log.warning('already processed all logged data, skipping'
				+ ' series defined by %s', optionsDict)
		return startDataIndex

	dataIndex = startDataIndex
	seriesTitle = optionsDict.get('title', logName)
	seriesData = allSeriesData.get(seriesTitle)
	if seriesData is None:
		seriesData = {}
		allSeriesData[seriesTitle] = seriesData

	previousDate = None
	lastDate = optionsDict.get('lastDate')
	if lastDate:
		lastDate = xh.datalogging.parseTimestamp(lastDate)

	while dataIndex < n:
		d, valueStr = logData[dataIndex]
		if lastDate is not None and d > lastDate:
			seriesData[lastDate + (d - lastDate)/2] = GAP_VALUE
			return dataIndex

		if mapFn:
			valueStr = mapFn(valueStr)
		seriesData[d] = valueStr
		if previousDate is not None and (d - previousDate) > GAP_DT:
			seriesData[previousDate+GAP_DT] = GAP_VALUE
		previousDate = d

		dataIndex += 1

	return dataIndex


def buildJsData(graphDefinitions, allLogData):
	"""
	Use graph definitions to transform log data into javascript blobs
	appropriate for Dygraph.
	"""
	seriesDefinitions = graphDefinitions['series']

	# Reorganize data to be categorized by series (name of a line on a graph
	# and not log (name of a data source, often an XBee).
	# Insert gap markers.
	allSeriesData = _buildSeriesData(seriesDefinitions, allLogData,
		graphDefinitions.get('map'))

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


