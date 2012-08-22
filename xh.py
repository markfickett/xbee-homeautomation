#!/usr/bin/python
"""%prog command [options]
Issue commands to or read data from the XBee Home Automation system.
Examples:
 $ xh # defualt: attach to the pysically connected Xbee and run plugins
 $ xh list # list information about available Xbees and plugins
 $ xh setup --plugin 'Temperature Logger' --serial 0x1a23
"""

import logging
log = logging.getLogger('xh')

import code, time, os
import xh
from xh.deps import serial, xbee
from xh.protocol import *
from yapsy.PluginManager import PluginManagerSingleton

LOCAL_SCRIPT = os.path.join(os.path.dirname(__file__), 'xh.local.py')
FRAME_LOGGER_NAME = 'Frame Logger'


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


log.debug('opened config')
INTERACT_BANNER = ('The xbee object is available as "xb". A received frame list'
	+ ' is available from the Frame Logger plugin, available as "fl".'
	+ ' Type control-D to exit.')

with xh.Config():
	log.debug('collecting plugins')
	xh.SetupUtil.CollectPlugins()
	fl = getFrameLoggerPlugin()
	xh.SetupUtil.SetLoggerRedisplayAfterEmit(logging.getLogger())
	with xh.SetupUtil.InitializedXbee() as xb:
		log.info('connected to locally attached Xbee')
		xh.protocol.Command.setXbeeSingleton(xb)
		with xh.SetupUtil.ActivatedPlugins():
			log.info('started')

			runLocalScript()

			xh.SetupUtil.RunPythonStartup()
			namespace = globals()
			namespace.update(locals())
			code.interact(banner=INTERACT_BANNER, local=namespace)

log.info('exiting')
