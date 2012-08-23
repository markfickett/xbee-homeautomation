#!/usr/bin/python
import argparse

parser = argparse.ArgumentParser(
formatter_class=argparse.RawDescriptionHelpFormatter,
description="""
Issue commands to or read data from the XBee Home Automation system.
Examples:
 $ %(prog)s run # attach to the pysically connected Xbee and run plugins
 $ %(prog)s list # list information about available Xbees and plugins
 $ %(prog)s setup --plugin 'Temperature Logger' --serial 0x1a23
"""
)

import logging
log = logging.getLogger('xh')

import code, time, os
import xh
from xh.deps import Enum, serial, xbee
from xh.protocol import *
from yapsy.PluginManager import PluginManagerSingleton

LOCAL_SCRIPT = os.path.join(os.path.dirname(__file__), 'xh.local.py')
FRAME_LOGGER_NAME = 'Frame Logger'

COMMAND = Enum(
	'list',
	'run',
	'setup',
)
parser.add_argument('--verbose', '-v', action='count')
parser.add_argument('--quiet', '-q', action='count')
parser.add_argument('command', choices=[str(c) for c in COMMAND])


def runLocalScript():
	if os.path.isfile(LOCAL_SCRIPT):
		log.info('running %s' % LOCAL_SCRIPT)
		execfile(LOCAL_SCRIPT)
	else:
		log.info('no local script to run at %s' % LOCAL_SCRIPT)


def getFrameLoggerPlugin():
	pm = PluginManagerSingleton.get()
	p = pm.getPluginByName(FRAME_LOGGER_NAME)
	return p.plugin_object


INTERACT_BANNER = ('The xbee object is available as "xb". A received frame list'
	+ ' is available from the Frame Logger plugin, available as "fl".'
	+ ' Type control-D to exit.')


def run():
	log.debug('collecting plugins')
	xh.SetupUtil.CollectPlugins()
	fl = getFrameLoggerPlugin()
	xh.SetupUtil.SetLoggerRedisplayAfterEmit(logging.getLogger())
	with xh.SetupUtil.InitializedXbee() as xb:
		log.info('connected to locally attached Xbee')
		xh.protocol.Command.SetXbeeSingleton(xb)
		with xh.SetupUtil.ActivatedPlugins():
			log.info('started')

			runLocalScript()

			xh.SetupUtil.RunPythonStartup()
			namespace = globals()
			namespace.update(locals())
			code.interact(banner=INTERACT_BANNER, local=namespace)

	log.info('exiting')


def listNodeIds():
	with xh.SetupUtil.InitializedXbee() as xb:
		xh.protocol.Command.SetXbeeSingleton(xb)

		try:
			nTimeoutResponse = xh.Synchronous.SendAndWait(
				xh.protocol.NodeDiscoveryTimeout())
		except xh.Synchronous.TimeoutError, e:
			log.error(str(e))
			return []
		nTimeoutMillis = nTimeoutResponse.getTimeoutMillis()

		nodeInfoResponses = xh.Synchronous.SendAndAccumulate(
			xh.protocol.NodeDiscover(),
			nTimeoutMillis / 1000.0)
		return [r.getNodeId() for r in nodeInfoResponses]


def list():
	xh.SetupUtil.CollectPlugins()
	pm = PluginManagerSingleton.get()
	pluginInfoStr = 'Plugins:'
	for p in pm.getAllPlugins():
		infos = ['%s (%s%s)'
			% (p.name, os.path.basename(p.path), os.path.sep)]
		if '?' not in p.version:
			infos.append('v' + p.version)
		if p.description is not None:
			infos.append(p.description)
		serials = p.plugin_object.getSerials()
		if serials:
			infos.append('Xbee'
				+ ('' if len(serials) is 1 else 's'))
			infos.append(', '.join(['0x%x' % s for s in serials]))
		pluginInfoStr += '\n\t' + ' '.join(infos)
	log.info(pluginInfoStr)

	try:
		nodeInfoList = listNodeIds()
	except:
		nodeInfoList = []

	nodeInfoStr = 'Xbees:'
	for n in nodeInfoList:
		lineStr = str(n)
		nodeInfoStr += '\n\t' + lineStr
	log.info(nodeInfoStr)


def setup():
	raise NotImplementedError()


COMMAND_TO_FN = {
	COMMAND.run: run,
	COMMAND.list: list,
	COMMAND.setup: setup,
}


LOG_LEVELS = [
	logging.FATAL,
	logging.CRITICAL,
	logging.ERROR,
	logging.WARNING,	# -q hides info (but still shows WARNING)
	logging.INFO,		# default
	logging.DEBUG,		# -v also shows debug
]


def setVerbosity(verbose, quiet):
	if verbose is not None and quiet is not None:
		parser.error(
			'Come now, verbose and quiet are mutually exclusive!')
	base = LOG_LEVELS.index(logging.INFO)
	verbosity = base + (verbose or 0) - (quiet or 0)
	if verbosity < 0:
		parser.error('%d Qs is all there is.' % base)
	elif verbosity >= len(LOG_LEVELS):
		maxVs = (len(LOG_LEVELS) - 1) - base
		parser.error('%d V%s is all the more verbose one can be.'
			% (maxVs, '' if maxVs == 1 else 's'))
	logging.getLogger().setLevel(LOG_LEVELS[verbosity])


def main():
	args = parser.parse_args()
	setVerbosity(args.verbose, args.quiet)
	command = xh.EnumUtil.FromString(COMMAND, args.command)
	with xh.Config():
		log.debug('opened config')
		COMMAND_TO_FN[command]()


main()
