#!/usr/bin/env python2.7
"""Run or query the XBee Home Automation system.

Examples:
Attach to the pysically connected XBee, run plugins and a Python interpreter.
 $ %(prog)s run
Print information about available XBees and plugins.
 $ %(prog)s list
"""

import argparse
import code
import logging
import os
import time

import network

import xh
from xh.deps import Enum, serial, xbee
from yapsy.PluginManager import PluginManagerSingleton


LOCAL_SCRIPT = os.path.join(os.path.dirname(__file__), 'xh.local.py')
FRAME_LOGGER_NAME = 'Frame Logger'

log = logging.getLogger('xh')

parser = argparse.ArgumentParser(
	formatter_class=argparse.RawDescriptionHelpFormatter,
	description=__doc__)


def runLocalScript():
	if os.path.isfile(LOCAL_SCRIPT):
		log.info('running %s' % LOCAL_SCRIPT)
		execfile(LOCAL_SCRIPT)
	else:
		log.info('no local script to run at %s' % LOCAL_SCRIPT)


def getFrameLoggerPlugin():
	pm = PluginManagerSingleton.get()
	p = pm.getPluginByName(FRAME_LOGGER_NAME)
	return p and p.plugin_object


INTERACT_BANNER = ('The xbee object is available as "xb". A received frame list'
	+ ' is available from the Frame Logger plugin, available as "fl".'
	+ ' Type control-D to exit.')


def run(args):
	log.debug('collecting plugins')
	if not args.noPlugins:
		xh.setuputil.collectPlugins()
	fl = getFrameLoggerPlugin()
	xh.setuputil.setLoggerRedisplayAfterEmit(logging.getLogger())
	serialDevice = (xh.setuputil.FAKE_SERIAL if args.fakeSerial
			else args.serialDevice)
	with xh.setuputil.initializedXbee(serialDevice=serialDevice) as xb:
		log.info('connected to locally attached XBee')
		xh.protocol.Command.setXbeeSingleton(xb)
		with (xh.util.noopContext() if args.noPlugins
				else xh.setuputil.activatedPlugins()):
			log.info('started')

			runLocalScript()

			xh.setuputil.runPythonStartup()
			namespace = globals()
			namespace.update(locals())
			code.interact(banner=INTERACT_BANNER, local=namespace)

	log.info('exiting')


def listNodeIds(serialDevice=None, timeout=None):
	with xh.setuputil.initializedXbee(serialDevice=serialDevice) as xb:
		xh.protocol.Command.setXbeeSingleton(xb)

		if timeout is None:
			try:
				nTimeoutResponse = xh.synchronous.sendAndWait(
					xh.protocol.NodeDiscoveryTimeout())
				sleepResponse = xh.synchronous.sendAndWait(
					xh.protocol.SleepPeriod())
			except xh.synchronous.TimeoutError, e:
				log.error(str(e))
				return []
			timeoutMillis = nTimeoutResponse.getTimeoutMillis()
			sleepMillis = sleepResponse.getPeriodMillis()
			if (sleepMillis != xh.protocol.SleepPeriod.
					DEFAULT_PERIOD_MILLIS):
				timeoutMillis += sleepMillis
				log.info('will wait an extra %dms for sleeping'
						+ ' devices', sleepMillis)
			timeout = timeoutMillis / 1000.0

		nodeInfoResponses = xh.synchronous.sendAndAccumulate(
			xh.protocol.NodeDiscover(),
			timeout)
		return [r.getNodeId() for r in nodeInfoResponses]


def list(args):
	xh.setuputil.collectPlugins()
	pm = PluginManagerSingleton.get()
	pluginInfoStr = 'Plugins:'
	for p in pm.getAllPlugins():
		infos = ['%s (%s%s)'
			% (p.name, os.path.basename(p.path), os.path.sep)]
		if '?' not in p.version:
			infos.append('v' + p.version)
		if p.description is not None:
			infos.append(p.description)
		pluginInfoStr += '\n\t' + ' '.join(infos)
	log.info(pluginInfoStr)

	serialDevice = (xh.setuputil.FAKE_SERIAL if args.fakeSerial
			else args.serialDevice)
	nodeInfoList = listNodeIds(
		serialDevice=serialDevice,
		timeout=args.timeout)

	nodeInfoStr = 'XBees:'
	for n in nodeInfoList:
		lineStr = str(n)
		nodeInfoStr += '\n\t' + lineStr
	log.info(nodeInfoStr)


LOG_LEVELS = [
	logging.FATAL,
	logging.CRITICAL,
	logging.ERROR,
	logging.WARNING,	# -q hides info (but still shows WARNING)
	logging.INFO,		# default
	logging.DEBUG,		# -v also shows debug
]


def setVerbosity(verbose, quiet):
	base = LOG_LEVELS.index(logging.INFO)
	verbosity = base + (verbose or 0) - (quiet or 0)
	if verbosity < 0:
		parser.error('%d Qs is all there is.' % base)
	elif verbosity >= len(LOG_LEVELS):
		maxVs = (len(LOG_LEVELS) - 1) - base
		parser.error('%d V%s is all the more verbose one can be.'
			% (maxVs, '' if maxVs == 1 else 's'))
	logging.getLogger().setLevel(LOG_LEVELS[verbosity])


def addCommonArguments(*subparsers):
	"""
	Add common options to all subparsers.

	This avoids the standard subcommand outcome, where some options have to
	go before the subcommand and some after (xh -v list --timeout 30), and
	instead allows all options to follow the subcommands
	(xh list -v --timeout 30).
	"""
	for subparser in subparsers:
		commonGroup = subparser.add_argument_group('common arguments')
		verbosityGroup = commonGroup.add_mutually_exclusive_group()
		verbosityGroup.add_argument('--verbose', '-v', action='count')
		verbosityGroup.add_argument('--quiet', '-q', action='count')
		serialGroup = commonGroup.add_mutually_exclusive_group()
		serialGroup.add_argument('--serial-device', dest='serialDevice',
			help='Device to use for local XBee communication.')
		serialGroup.add_argument('--fake-serial', dest='fakeSerial',
			action='store_true',
			help='Use a fake XBee object and do not look for or'
			+ ' open a serial device.')


def main():
	args = parser.parse_args()
	setVerbosity(args.verbose, args.quiet)
	xh.setuputil.setDependenciesLoggingLevel(logging.WARNING)
	with xh.Config():
		log.debug('opened config')
		args.func(args)


subparsers = parser.add_subparsers(title='commands')

runParser = subparsers.add_parser('run')
runParser.set_defaults(func=run)
runParser.add_argument('--no-plugins', action='store_true', dest='noPlugins',
	help='Do not load or activate any plugins.')

listParser = subparsers.add_parser('list')
listParser.set_defaults(func=list)
listParser.add_argument('--timeout', '-t', type=float,
	help='Timeout (in seconds, fractional ok) to wait for XBee responses. '
		'Useful if sleeping nodes will not respond within the default '
		'ND timeout, NT.')

netParser = network.addSubparser(subparsers)

addCommonArguments(runParser, listParser, netParser)


if __name__ == '__main__':
	main()
