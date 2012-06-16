def FromString(enumeration, s):
	"""
	@return the enumeration value which matches the given string.
	@throw ValueError if no match is found.
	"""
	for e in enumeration:
		if str(e) == s:
			return e
	raise ValueError('No value "%s" in %s.' % (s, enumeration))
