import logging
logging.basicConfig(
        format='[%(levelname)s %(name)s] %(message)s',
        level=logging.DEBUG)

import deps

import Config, EnumUtil
import Encoding
import Util

import protocol
