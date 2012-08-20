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

import code, readline, time, os
import xh
from xh.deps import serial, xbee, pysignals
from xh.protocol import *

FRAME_HISTORY_LIMIT = 700
FRAME_HISTORY_TRIM = 500
LOCAL_SCRIPT = os.path.join(os.path.dirname(__file__), 'xh.local.py')

global fr
fr = []
@pysignals.receiver(xh.Signals.FrameReceived)
def logFrame(sender=None, signal=None, frame=None):
	global fr

	log.info('received %s' % frame)
	readline.redisplay()

	fr.insert(0, frame)
	if len(fr) > FRAME_HISTORY_LIMIT:
		fr = fr[:FRAME_HISTORY_TRIM]


def runLocalScript():
	if os.path.isfile(LOCAL_SCRIPT):
		log.info('running %s' % LOCAL_SCRIPT)
		execfile(LOCAL_SCRIPT)
	else:
		log.info('no local script to run at %s' % LOCAL_SCRIPT)


with xh.SetupUtil.InitializedXbee() as xb:
	log.info('started')

	runLocalScript()

	xh.SetupUtil.RunPythonStartup()
	namespace = globals()
	namespace.update(locals())
	code.interact(banner='The xbee object is available as "xb".'
		+ ' A received frame list is available as "fr".'
		+ ' Type control-D to exit.',
		local=namespace)

log.info('exiting')
