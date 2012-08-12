#!/usr/bin/python
"""%prog command [options]
Issue commands to or read data from the XBee Home Automation system.
Examples:
 $ xh info # print information about a physically connected XBee
 $ xh init # initialize network PANID and encryption key
 $ xh setup --name 'Living Room' # set up and name a new sensor/control
"""

import logging
log = logging.getLogger('xh')

import code, optparse, os, readline, sys, time
import xh
from xh.protocol import Command, NodeDiscover, Data
from xh.deps import serial, xbee

def runPythonStartup():
	"""
	Run the $PYTHONSTARTUP script, if available, to prepare for an
	interactive prompt.
	"""
	startup = os.getenv('PYTHONSTARTUP')
	if startup:
		with open(startup) as startupFile:
			exec(startupFile.read())

global fr
fr = []
FRAME_HISTORY_LIMIT = 700
FRAME_HISTORY_TRIM = 500
def logData(rawData):
	global fr
	try:
		frame = xh.protocol.ParseFromDict(rawData)
		fr.append(frame)
		log.info('received %s' % frame)
		if len(fr) > FRAME_HISTORY_LIMIT:
			fr = fr[:FRAME_HISTORY_TRIM]
	except:
		log.error('error handling data: %s' % rawData, exc_info=True)
	readline.redisplay()


with xh.Util.InitializedXbee(callback=logData) as xb:
	log.info('started')
	"""
	for cmd in (
		Command(Command.NAME.MY),
		Command(Command.NAME.ID),
		Command(Command.NAME.KY),
		Command(Command.NAME.EE),
		Command(Command.NAME.SH),
		Command(Command.NAME.SL),
		Command(Command.NAME.NI),
		Command(Command.NAME.__getattribute__('%V')),
		Command(Command.NAME.NT),
		NodeDiscover(),
		Command(Command.NAME.__getattribute__('%V'),
			dest=0x13a200408cca0e),
	):
		cmd.send(xb)
	"""
	runPythonStartup()
	namespace = locals()
	namespace.update(globals())
	code.interact(banner='The xbee object is available as "xb".'
		+ ' A received frame list is available as "fr".'
		+ ' Type control-D to exit.',
		local=namespace)

log.info('exiting')
