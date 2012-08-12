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

import sys, os, time, optparse
import xh
from xh.protocol import Command, NodeDiscover, Data
from xh.deps import serial, xbee

DATA_LOG_FILE = 'datalog.csv'
log.info('also logging CSV to %s' % DATA_LOG_FILE)

log.info('started')
log.info('Type control-C to exit.')

def logData(rawData):
	try:
		frame = xh.protocol.ParseFromDict(rawData)
		log.info('received %s' % frame)
		if isinstance(frame, Data):
			with open(DATA_LOG_FILE, 'a') as dataFile:
				fields = []
				fields.append(frame.formatTimestamp())
				for s in frame.getSamples():
					fields.append(str(s.getVolts()))
				dataFile.write(','.join(fields) + '\n')
				
	except:
		log.error('error handling data: %s' % rawData, exc_info=True)


with xh.Util.InitializedXbee(callback=logData) as xb:
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
	while True:
		time.sleep(0.02)

log.info('exiting')
