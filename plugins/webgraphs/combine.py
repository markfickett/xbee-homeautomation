import collections
import datetime
import json
import logging

import xh


log = logging.getLogger('webgraphs.combine')
TIMESTAMP_COLUMN_HEADER = 'Timestamp'
GAP_VALUE = 'datagap'
GAP_DT = datetime.timedelta(minutes=10)
EPOCH = datetime.datetime.utcfromtimestamp(0)
_UNUSEDS_TITLE = 'Unconfigured'
_UNUSEDS_VAR_NAME = 'unconfigured'


def _getEpochMillis(d):
	delta = d - EPOCH
	return delta.total_seconds() * 1000


def _getJsDateString(d):
	return 'new Date(%d)' % _getEpochMillis(d)


def _buildSeriesData(seriesDefinitions, allLogData, parseFn, mapFn):
	"""
	Convert from log data, named by data source, of the form:
		{ loggedName: [ datetime: rawValueStr, ... ], ...  }
	to series data, with semantic names and mapped values, of the form:
		{ seriesName: { datetime: mappedValueStr, ... }, ... }
	Also insert gap markers (GAP_VALUE) where no data was logged for GAP_DT.
	"""
	allSeriesData = collections.defaultdict(dict)
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
					parseFn, mapFn, dataStartIndex)

		n = len(logData)
		if dataStartIndex < n:
			log.warning('only used %d of %d entries for %s.',
					dataStartIndex, n, logName)

	return allSeriesData


def _addToSeriesData(allSeriesData, optionsDict, logName, logData,
		parseFn, mapFn, startDataIndex):
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
	seriesData = allSeriesData[seriesTitle]

	lastDate = optionsDict.get('lastDate')
	if lastDate:
		lastDate = xh.datalogging.parseTimestamp(lastDate)

	# Assemble the function to parse the log value (a string), do any
	# series-specific and graph-specific mappings, and the format it as
	# a string again for javascript.
	preMapFn = optionsDict.get('preMap')
	if preMapFn:
		if mapFn:
			parseAndMapFn = lambda s: str(mapFn(
					preMapFn(parseFn(s))))
		else:
			parseAndMapFn = lambda s: str(preMapFn(parseFn(s)))
	else:
		if mapFn:
			parseAndMapFn = lambda s: str(mapFn(parseFn(s)))
		else:
			parseAndMapFn = lambda s: str(parseFn(s))

	while dataIndex < n:
		d, valueStr = logData[dataIndex]
		if lastDate is not None and d > lastDate:
			seriesData[lastDate + (d - lastDate)/2] = GAP_VALUE
			return dataIndex

		seriesData[d] = parseAndMapFn(valueStr)

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
	parseFn = graphDefinitions.get('parse', float)
	mapFn = graphDefinitions.get('map')
	allSeriesData = _buildSeriesData(seriesDefinitions, allLogData,
		parseFn, mapFn)

	seriesTitles = allSeriesData.keys()
	numSeries = len(seriesTitles)
	# Build a combined dict of {date object: (row entries)}.
	# Insert gap markers.
	def makeRowFn():
		return [None] * numSeries
	rowData = collections.defaultdict(makeRowFn)
	for seriesName, seriesValuesDict in allSeriesData.iteritems():
		seriesIndex = seriesTitles.index(seriesName)
		prevD = None
		for d, v in sorted(seriesValuesDict.items()):
			if prevD is not None and (d - prevD > GAP_DT):
				rowData[prevD + GAP_DT][seriesIndex] = GAP_VALUE
			rowData[d][seriesIndex] = v
			prevD = d

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
	for annotationDict in graphDefinitions.get('annotations', []):
		d = dict(annotationDict)
		d['x'] = _getEpochMillis(xh.datalogging.parseTimestamp(d['x']))
		annotationsParsed.append(d)
	annotationJsStr = json.dumps(annotationsParsed)
	
	return labelsJsStr, dataJsStr, annotationJsStr


def addGraphForUnusedData(graphConfigs, dataKeys):
	"""
	Add a graph config for all the dataKeys (from logs) which are not
	otherwise used.
	"""
	usedDataKeys = set()
	for name, graphConfig in graphConfigs:
		usedDataKeys.update(set(graphConfig.get('series', {}).keys()))
	unusedDataKeys = set(dataKeys)
	unusedDataKeys.difference_update(usedDataKeys)
	if not unusedDataKeys:
		return

	log.warning('creating graph of raw values for unconfigured '
			+ 'log data sets: %s', unusedDataKeys)
	unusedsConfig = {
		'title': _UNUSEDS_TITLE,
		'series': dict([(k, [{}]) for k in unusedDataKeys]),
	}
	graphConfigs.append((_UNUSEDS_VAR_NAME, unusedsConfig))


