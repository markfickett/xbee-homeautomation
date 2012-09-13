import contextlib



def invertedDict(d):
	return dict([(v, k) for k, v in d.iteritems()])


def invertedDictWithRepeatedValues(d):
	"""
	@return a dict where each value in the original maps to a tuple of the
		values in the original map which mapped to it
	"""
	o = {}
	for k, v in d.iteritems():
		keys = o.get(v, ())
		keys = keys + (k,)
		o[v] = keys
	return o


@contextlib.contextmanager
def noopContext():
	yield None

