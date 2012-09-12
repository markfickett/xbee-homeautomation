#!/usr/bin/env python
"""Run or query the XBee Home Automation system.

Examples:
Attach to the pysically connected XBee, run plugins and a Python interpreter.
 $ %(prog)s run
Print information about available XBees and plugins.
 $ %(prog)s list
Associate an XBee (by serial number) with a plugin.
 $ %(prog)s setup --plugin 'Temperature Logger' --serial 0x0013a200abcd1234
"""

import argparse
import code
import logging
import os
import time

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
	if not args.noplugins:
		xh.setuputil.CollectPlugins()
	fl = getFrameLoggerPlugin()
	xh.setuputil.SetLoggerRedisplayAfterEmit(logging.getLogger())
	with xh.setuputil.InitializedXbee(serialDevice=args.serialDevice) as xb:
		log.info('connected to locally attached XBee')
		xh.protocol.Command.SetXbeeSingleton(xb)
		with (xh.util.NoopContext() if args.noplugins
				else xh.setuputil.ActivatedPlugins()):
			log.info('started')

			runLocalScript()

			xh.setuputil.RunPythonStartup()
			namespace = globals()
			namespace.update(locals())
			code.interact(banner=INTERACT_BANNER, local=namespace)

	log.info('exiting')


def listNodeIds(serialDevice=None, timeout=None):
	with xh.setuputil.InitializedXbee(serialDevice=serialDevice) as xb:
		xh.protocol.Command.SetXbeeSingleton(xb)

		if timeout is None:
			try:
				nTimeoutResponse = xh.synchronous.SendAndWait(
					xh.protocol.NodeDiscoveryTimeout())
			except xh.synchronous.TimeoutError, e:
				log.error(str(e))
				return []
			nTimeoutMillis = nTimeoutResponse.getTimeoutMillis()
			timeout = nTimeoutMillis / 1000.0

		nodeInfoResponses = xh.synchronous.SendAndAccumulate(
			xh.protocol.NodeDiscover(),
			timeout)
		return [r.getNodeId() for r in nodeInfoResponses]


def list(args):
	xh.setuputil.CollectPlugins()
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
			infos.append('XBee'
				+ ('' if len(serials) is 1 else 's'))
			infos.append(', '.join(['0x%x' % s for s in serials]))
		pluginInfoStr += '\n\t' + ' '.join(infos)
	log.info(pluginInfoStr)

	try:
		nodeInfoList = listNodeIds(
			serialDevice=args.serialDevice,
			timeout=args.timeout)
	except:
		log.debug('error listing available XBees', exc_info=True)
		nodeInfoList = []

	nodeInfoStr = 'XBees:'
	for n in nodeInfoList:
		lineStr = str(n)
		nodeInfoStr += '\n\t' + lineStr
	log.info(nodeInfoStr)


def setup(args):
	if args.plugin is None:
		parser.error('Must specify plugin for setup.')
	if args.clear == bool(args.serial):
		parser.error(
			'Must either clear or supply serial numbers for setup.')

	xh.setuputil.CollectPlugins()
	pm = PluginManagerSingleton.get()
	pluginInfo = pm.getPluginByName(args.plugin)
	if pluginInfo is None:
		parser.error('No plugin named %r.' % args.plugin)
	pluginObj = pluginInfo.plugin_object
	if args.clear:
		pluginObj.clearSerials()
	else:
		serials = set(args.serial)
		if not args.replace:
			serials = serials.union(pluginObj.getSerials())
		pluginObj.setSerials(serials)


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


def main():
	args = parser.parse_args()
	setVerbosity(args.verbose, args.quiet)
	with xh.Config():
		log.debug('opened config')
		args.func(args)


def dec_or_hex_int(string):
	if string.isdigit():
		return int(string)
	else:
		return int(string, 16)

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
		commonGroup.add_argument('--serial-device', dest='serialDevice',
			help='Device to use for local XBee communication.')

subparsers = parser.add_subparsers(title='commands')

runParser = subparsers.add_parser('run')
runParser.set_defaults(func=run)
runParser.add_argument('--no-plugins', action='store_true', dest='noplugins',
	help='Do not load or activate any plugins.')

listParser = subparsers.add_parser('list')
listParser.set_defaults(func=list)
listParser.add_argument('--timeout', '-t', type=float,
	help='Timeout (in seconds, fractional ok) to wait for XBee responses. '
		'Useful if sleeping nodes will not respond within the default '
		'ND timeout, NT.')

setupParser = subparsers.add_parser('setup')
setupParser.set_defaults(func=setup)
setupParser.add_argument('plugin', help='The name of a plugin.')
setupParser.add_argument('--clear', '-c', action='store_true',
	help='Clear all XBee-plugin associations.')
setupParser.add_argument('--serial', '-s', type=dec_or_hex_int, action='append',
	help='The serial number (hex or decimal) of an XBee module.'
	+ ' May be repated.')
setupParser.add_argument('--replace', '-r', action='store_true',
	help='Replace all existing XBee-plugin associations.'
	+ 'By default, adds a new association.')

addCommonArguments(runParser, listParser, setupParser)


main()
