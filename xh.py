#!/usr/bin/env python
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
import random
import time

import xh
from xh.deps import Enum, serial, xbee
from yapsy.PluginManager import PluginManagerSingleton


LOCAL_SCRIPT = os.path.join(os.path.dirname(__file__), 'xh.local.py')
FRAME_LOGGER_NAME = 'Frame Logger'
PAN_ID_BITS = 14 # ID command accepts <= 0x3FFF, rejects greater values
LINK_KEY_BITS = 128

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

def _setNetworkParams(panId, linkKey):
	"""
	Set the network parameters of the locally connected device.
	@param panId: 16-bit network ID
	@param linkKey: 128-bit link encryption key, or None for no encryption
	"""
	keyMsg = ('No encryption.' if linkKey is None
			else ('Link key: 0x%X' % linkKey))
	log.info('Will set PAN ID: 0x%X %s' % (panId, keyMsg))

	commands = []

	setIdCmd = xh.protocol.Command(xh.protocol.Command.NAME.ID)
	setIdCmd.setParameter(panId)
	commands.append(setIdCmd)

	eeCmd = xh.protocol.EncryptionEnable()
	eeCmd.setEnabled(linkKey is not None)
	commands.append(eeCmd)

	if linkKey is not None:
		keyCmd = xh.protocol.Command(xh.protocol.Command.NAME.KY)
		keyCmd.setParameter(linkKey)
		commands.append(keyCmd)

	commands.append(xh.protocol.Write())

	for cmd in commands:
		xh.synchronous.sendAndWait(cmd)

	log.info('Done.')


def _setNetworkParamsFromArgs(validArgs):
	if validArgs.generate:
		_setNetworkParams(
			random.getrandbits(PAN_ID_BITS),
			random.getrandbits(LINK_KEY_BITS)
					if validArgs.genKey else None)
	else:
		_setNetworkParams(validArgs.panId, validArgs.linkKey)


def _listNetworkParams():
	"""
	Print (via logging) previously used network parameters.
	"""


def setUpNetwork(args):
	if args.genKey and not args.generate:
		parser.error('--use-encryption must be used with --generate')
	if args.linkKey and not args.panId:
		parser.error('--link-key must be used with --pan-id')
	if ((args.generate or args.genKey)
			and (args.linkKey or args.panId)):
		parser.error('Must either --generate new network parameters '
			'(optionally with --use-encryption) '
			'or specify --pan-id (and optionally --link-key).')

	if args.generate or args.panId:
		with xh.setuputil.initializedXbee() as xb:
			log.info('connected to locally attached XBee')
			xh.protocol.Command.setXbeeSingleton(xb)
			_setNetworkParamsFromArgs(args)
	else:
		_listNetworkParams()


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

netParser = subparsers.add_parser('network',
	help='Set up network parameters for the local device. With no '
		'arguments, lists previously-used network parameters.')
netParser.set_defaults(func=setUpNetwork)
netParser.add_argument('--generate', action='store_true',
	help='Generate (and use, print, and store) a PAN ID.')
netParser.add_argument('--use-encryption', action='store_true', dest='genKey',
	help='When using --generate to make new network parameters, also '
		'generate a network encryption key.')
netParser.add_argument('--pan-id', type=dec_or_hex_int, dest='panId',
	help='%d-bit PAN ID of the network (ATID), for example 1B37'
		% PAN_ID_BITS)
netParser.add_argument('--link-key', type=dec_or_hex_int, dest='linkKey',
	help=('%d-bit Link encryption key (ATKY). Setting this also implies '
		' enabling encryption (ATEE1).') % LINK_KEY_BITS)

addCommonArguments(runParser, listParser, netParser)


if __name__ == '__main__':
	main()
