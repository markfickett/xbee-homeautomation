"""
Subcommand for setting (or listing) network parameters.
"""

import logging
import random

import xh


log = logging.getLogger('xh network')

_CONFIG_SECTION = 'xh.network'
_CONFIG_COUNT = 'num'
_CONFIG_PAN_ID_T = 'panid%d'
_CONFIG_KEY_T = 'key%d'
_CONFIG_NO_KEY_VALUE = -1

PAN_ID_BITS = 14 # ID command accepts <= 0x3FFF, rejects greater values
LINK_KEY_BITS = 128


def dec_or_hex_int(string):
	if string.isdigit():
		return int(string)
	else:
		return int(string, 16)


def addSubparser(subparsers):
	netParser = subparsers.add_parser('network',
		help='Set up network parameters for the local device. With no '
			'arguments, lists previously-used network parameters.')
	netParser.set_defaults(func=_setUpNetwork)
	netParser.add_argument('--generate', action='store_true',
		help='Generate (and use, print, and store) a PAN ID.')
	netParser.add_argument('--use-encryption', action='store_true',
		dest='genKey',
		help='When using --generate to make new network parameters, '
			'also generate a network encryption key.')
	netParser.add_argument('--pan-id', type=dec_or_hex_int, dest='panId',
		help='%d-bit PAN ID of the network (ATID), for example 1B37'
			% PAN_ID_BITS)
	netParser.add_argument('--link-key', type=dec_or_hex_int,
		dest='linkKey',
		help=('%d-bit Link encryption key (ATKY). Setting this also '
			'implies enabling encryption (ATEE1).') % LINK_KEY_BITS)
	return netParser


def _addConfigEntry(panId, linkKey):
	existingEntries = set(_getConfigEntries())
	if (panId, linkKey) in existingEntries:
		return

	config = xh.Config.get()
	if not config.has_section(_CONFIG_SECTION):
		config.add_section(_CONFIG_SECTION)
		n = 0
	else:
		n = config.getint(_CONFIG_SECTION, _CONFIG_COUNT)

	config.set(_CONFIG_SECTION, _CONFIG_PAN_ID_T % n, str(panId))
	key = linkKey if linkKey is not None else _CONFIG_NO_KEY_VALUE
	config.set(_CONFIG_SECTION, _CONFIG_KEY_T % n, str(key))

	n += 1
	config.set(_CONFIG_SECTION, _CONFIG_COUNT, str(n))


def _getConfigEntries():
	config = xh.Config.get()
	entries = []
	if not config.has_section(_CONFIG_SECTION):
		return entries
	n = config.getint(_CONFIG_SECTION, _CONFIG_COUNT)
	for i in xrange(n):
		panId = config.getint(_CONFIG_SECTION, _CONFIG_PAN_ID_T % i)
		key = config.getint(_CONFIG_SECTION, _CONFIG_KEY_T % i)
		if key == _CONFIG_NO_KEY_VALUE:
			key = None
		entries.append((panId, key))
	return entries


def _setNetworkParams(panId, linkKey):
	"""
	Set the network parameters of the locally connected device.
	@param panId: 16-bit network ID
	@param linkKey: 128-bit link encryption key, or None for no encryption
	"""
	keyMsg = ('No encryption.' if linkKey is None
			else ('Link key: 0x%x' % linkKey))
	log.info('Will set PAN ID: 0x%x %s' % (panId, keyMsg))

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

	_addConfigEntry(panId, linkKey)

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
	entries = _getConfigEntries()
	if not entries:
		log.info('No network information in config.')
		return
	for panId, linkKey in entries:
		linkMsg = ('No encryption.' if linkKey is None
			else 'Link key 0x%x' % linkKey)
		log.info('PAN ID 0x%x %s' % (panId, linkMsg))


def _setUpNetwork(args):
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


