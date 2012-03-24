"""QuickCheck."""

from qc.state import arbfun, reset
from qc.arbitrary import name, nameUtf8, fromList
import arbitrary as _arb
import util as _util

import os, sys
import itertools
import random


def property(fn):
  """QuickCheck property decorator. Wrap a function with this to turn it into a
  QuickCheck test."""
  def test_property(*args, **kwargs):
    reset()
    for _ in xrange(100):
      fn(*args, **kwargs)
  test_property.__name__ = fn.__name__
  return test_property


################################################################################
## ARBITRARY FUNCTIONS: Names may clash with builtin names.
################################################################################


@arbfun
def int(low=(-sys.maxint-1), high=sys.maxint):
  """An arbitrary integer."""
  return _arb.Int(low, high)


@arbfun
def long(low=(-sys.maxint*2), high=sys.maxint*2):
  """An arbitrary long."""
  return _arb.Int(low, high)


@arbfun
def float(low=-10e10, high=10e10):
  """An arbitrary float."""
  return _arb.Float(low, high)


@arbfun
def randstr(length=None, maxlen=sys.maxint):
  """A random string, optionally with a constant or maximum length."""
  if length is not None:
    return (os.urandom(length) for _ in itertools.repeat(0))
  else:
    return _arb.RandomString(maxlen)


def _str(length, maxlen):
  """Internal string getter."""
  if length is not None:
    return randstr(length)
  elif maxlen is not None:
    s = _arb.longstr()
    if len(s) < maxlen:
      return s
    s = _arb.shortstr()
    if len(s) < maxlen:
      return s
    return randstr(maxlen=maxlen)
  else:
    if random.random() < 0.5:
      return _arb.shortstr()
    else:
      return _arb.longstr()


@arbfun
def str(length=None, maxlen=None):
  """An arbitrary string. UTF-8 encoded."""
  while True:
    yield _util.utf8(_str(length, maxlen))


@arbfun
def unicode(length=None, maxlen=None):
  """An arbitrary string. UTF-8 encoded."""
  while True:
    yield _util.fromUtf8(_str(length, maxlen))
