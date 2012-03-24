"""QuickCheck random generator set state."""

import traceback
import hashlib
import functools


# Map from (type, args, kwargs, SHA1(str(traceback))) to generator functions
GENERATORS = {}
# Map from type string to generator function
TYPES = {}


def getGenerator(t, *args, **kwargs):
  """Get the next thing in the t(*args, **kwargs) stream."""
  hasher = hashlib.sha1(); map(hasher.update, traceback.format_stack())
  spec = (t, args, tuple(sorted(kwargs.items())), hasher.digest())
  if spec not in GENERATORS:
    try:
      genfun = TYPES[t]
    except KeyError:
      raise NameError('Unknown generator type %r' % t)
    GENERATORS[spec] = genfun(*args, **kwargs)
  return GENERATORS[spec].next()


def arbfun(fn):
  """Decorator @arbfun) takes a function that returns an iterator, and returns a function
  that gets that generator from the generator registry."""
  TYPES[fn.__name__] = fn
  return functools.partial(getGenerator, fn.__name__)


def reset():
  """Reset the state."""
  global GENERATORS
  GENERATORS = {}
