"""Internal utility stuff."""

def utf8(s):
  """Convert s to UTF-8 if necessary."""
  if isinstance(s, unicode):
    return s.encode('utf8')
  else:
    return str(s)


def fromUtf8(s):
  """Convert s from UTF-8 if necessary."""
  if isinstance(s, str):
    return s.decode('utf8')
  else:
    return unicode(s)
