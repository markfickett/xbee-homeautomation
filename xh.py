#!/usr/bin/python
"""Run or query the Xbee Home Automation system.

Examples:
Attach to the pysically connected Xbee, run plugins and a Python interpreter.
 $ %(prog)s run
Print information about available Xbees and plugins.
 $ %(prog)s list
Associate an Xbee (by serial number) with a plugin.
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
	return p.plugin_object


INTERACT_BANNER = ('The xbee object is available as "xb". A received frame list'
	+ ' is available from the Frame Logger plugin, available as "fl".'
	+ ' Type control-D to exit.')


def run(args):
	log.debug('collecting plugins')
	xh.setuputil.CollectPlugins()
	fl = getFrameLoggerPlugin()
	xh.setuputil.SetLoggerRedisplayAfterEmit(logging.getLogger())
	with xh.setuputil.InitializedXbee() as xb:
		log.info('connected to locally attached Xbee')
		xh.protocol.Command.SetXbeeSingleton(xb)
		with xh.setuputil.ActivatedPlugins():
			log.info('started')

			runLocalScript()

			xh.setuputil.RunPythonStartup()
			namespace = globals()
			namespace.update(locals())
			code.interact(banner=INTERACT_BANNER, local=namespace)

	log.info('exiting')


def listNodeIds():
	with xh.setuputil.InitializedXbee() as xb:
		xh.protocol.Command.SetXbeeSingleton(xb)

		try:
			nTimeoutResponse = xh.synchronous.SendAndWait(
				xh.protocol.NodeDiscoveryTimeout())
		except xh.synchronous.TimeoutError, e:
			log.error(str(e))
			return []
		nTimeoutMillis = nTimeoutResponse.getTimeoutMillis()

		nodeInfoResponses = xh.synchronous.SendAndAccumulate(
			xh.protocol.NodeDiscover(),
			nTimeoutMillis / 1000.0)
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


verbosityGroup = parser.add_mutually_exclusive_group()
verbosityGroup.add_argument('--verbose', '-v', action='count')
verbosityGroup.add_argument('--quiet', '-q', action='count')

subparsers = parser.add_subparsers(title='commands')

runParser = subparsers.add_parser('run')
runParser.set_defaults(func=run)

listParser = subparsers.add_parser('list')
listParser.set_defaults(func=list)

setupParser = subparsers.add_parser('setup')
setupParser.set_defaults(func=setup)
setupParser.add_argument('plugin', help='The name of a plugin.')
setupParser.add_argument('--clear', '-c', action='store_true',
	help='Clear all Xbee-plugin associations.')
setupParser.add_argument('--serial', '-s', type=dec_or_hex_int, action='append',
	help='The serial number (hex or decimal) of an Xbee module.'
	+ ' May be repated.')
setupParser.add_argument('--replace', '-r', action='store_true',
	help='Replace all existing Xbee-plugin associations.'
	+ 'By default, adds a new association.')


main()
