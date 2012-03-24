"""QuickCheck."""

from qc.state import arbfun
from qc.arbitrary import name, nameUtf8
from qc import arbitrary as _arb

import os, sys
import itertools


################################################################################
## WRAPPER FUNCTIONS: Wrap useful classes with clashy names.
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
