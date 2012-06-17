__all__ = [
	'DEVICE_TYPE',
]

from ..deps import Enum


DEVICE_TYPE = Enum(
	'COORDINATOR',	# must be index 0
	'ROUTER',	# 1
	'END_DEVICE',	# 2
)

