import BaseHTTPServer
import json
import logging
import os
import threading

import xh

import combine
import graphconfig
import templates


log = logging.getLogger('webgraph.Server')
HOST_NAME = '' # accessable by any name
PORT_NUMBER = 25563

RESPONSE_OK = 200
RESPONSE_NOT_FOUND = 404
HEADER_CONTENT_TYPE = 'Content-type'
CONTENT_TYPE_HTML = 'text/html'



class Server(xh.Plugin):
	def __init__(self):
		xh.Plugin.__init__(self)
		graphconfig.checkForLocalConfig()


	def activate(self):
		xh.Plugin.activate(self)

		def handleDataLoggedCb(sender=None, signal=None, **kwargs):
			self._dataLogged(**kwargs)
		xh.signals.DATA_LOGGED.connect(handleDataLoggedCb)
		self.__handleDataLoggedCb = handleDataLoggedCb

		self.__httpdStoppedEvent = threading.Event()

		self.__httpd = BaseHTTPServer.HTTPServer(
				(HOST_NAME, PORT_NUMBER), _HttpHandler)
		self.__httpd.xhdata = {}
		self._readExistingLogs()
		self.__httpd.xhdataLock = threading.Lock()
		self.__httpdThread = threading.Thread(
				target=self.runHttpdUntilStopped)
		self.__httpdThread.daemon = True
		self.__httpdThread.start()


	def deactivate(self):
		log.debug('deactivating')
		self.__httpd.shutdown()
		self.__httpdStoppedEvent.wait()
		log.debug('httpd server has stopped')

		xh.Plugin.deactivate(self)


	def runHttpdUntilStopped(self):
		log.info('listening at http://%s:%d',
				HOST_NAME or '*', PORT_NUMBER)
		self.__httpd.serve_forever()
		self.__httpd.server_close()
		self.__httpdStoppedEvent.set()


	def _readExistingLogs(self):
		log.debug('reading existing logs')
		for name, path in xh.datalogging.getLogFileNames().iteritems():
			with open(path) as logFile:
				log.debug('reading %s', path)
				self.__fillDataFromLog(name, logFile)
		log.debug('done')


	def __fillDataFromLog(self, name, logFile):
		self.__httpd.xhdata[name] = xh.datalogging.parseLogFile(logFile)


	def _dataLogged(self, name=None, value=None, timestamp=None,
			formattedValue=None, formattedTimestamp=None,
			serial=None, pinName=None):
		with self.__httpd.xhdataLock:
			d = self.__httpd.xhdata.get(name)
			if d is None:
				d = []
				self.__httpd.xhdata[name] = d
			d.append((timestamp, formattedValue))



class _HttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path == '/':
			return self.__handleMainPage()
		else:
			self.send_response(RESPONSE_NOT_FOUND)
			self.end_headers()


	def __sendOkHeaders(self):
		self.send_response(RESPONSE_OK)
		self.send_header(HEADER_CONTENT_TYPE, CONTENT_TYPE_HTML)
		self.end_headers()


	def __handleMainPage(self):
		self.__sendOkHeaders()

		with self.server.xhdataLock:
			data = dict(self.server.xhdata)
		graphConfigs, localHtml = graphconfig.getConfigsAndHtml()
		combine.addGraphForUnusedData(graphConfigs, data.keys())

		numPoints = sum([len(d) for d in data.values()])
		log.debug('building %d graphs from %d points in %d datasets',
				len(graphConfigs), numPoints, len(data))

		chartDivs = ''
		for name, _ in graphConfigs:
			chartDivs += templates.CHART_DIV % name
		drawCallsJsStr = ''
		annotationsJsStr = ''
		for name, valueDict in graphConfigs:
			labelsJsStr, dataJsStr, annJsStr = combine.buildJsData(
					valueDict, data)
			drawCallsJsStr += templates.DRAW_CALL % {
				'name': name,
				'title': json.dumps(valueDict['title']),
				'dataJs': dataJsStr,
				'labelJs': labelsJsStr,
			}
			annotationsJsStr += templates.ANNOTATIONS % {
				'name': name,
				'dataJs': annJsStr,
			}
		self.wfile.write(templates.MAIN_PAGE % {
			'localHtml': localHtml or '',
			'chartDivsHtml': chartDivs,
			'drawCallsJs': drawCallsJsStr,
			'annotationsJs': annotationsJsStr
		})


	def log_message(self, format, *args):
		log.info(format, *args)

