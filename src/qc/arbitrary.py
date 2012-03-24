"""Arbitrary value generators are infinite iterators."""

import os, sys
import random
import itertools

from qc.state import arbfun

FLOAT_MAX =  1.7976931348623157e+308
FLOAT_MIN = -1.7976931348623157e+308
FLOAT_EPS = 2.2204460492503131e-16

################################################################################
## LOW-LEVEL GENERATORS: Explicitly deal with state.
################################################################################



class Arbitrary(object):
  """An object that generates a stream of arbitrary data. The only API you actually need
  to follow is the iterator API."""

  # Probability of generating a tricky item instead of a normal one.
  trickyProbability = 0.1


  def __iter__(self):
    return self


  def next(self):
    """Get a value."""
    if random.random() < self.trickyProbability:
      return self.getTricky()
    else:
      return self.getNormal()


  def getTricky(self):
    """Get a tricky item."""
    raise NotImplementedError


  def getNormal(self):
    """Get a normal item."""
    raise NotImplementedError



class WithTrickySet(Arbitrary):
  """An Arbitrary object with a tricky list and a random function.

  Initially it will play through a deterministic-ish bootstrap sequence, then it will go
  to mostly random values."""

  def __init__(self, tricky=None):
    Arbitrary.__init__(self)
    self.tricky = (tricky or [])[::]
    # Bootstrap sequence: [tricky][tricky shuffled randomly]
    trickyShuffled = self.tricky[::]
    random.shuffle(trickyShuffled)
    self.bootstrapSequence = (self.tricky + trickyShuffled)[::-1]


  def getTricky(self):
    """Get a tricky item."""
    return self.tricky and random.choice(self.tricky)


  def getNormal(self):
    """Get a normal item."""
    raise NotImplementedError


  def next(self):
    """Get a value."""
    if self.bootstrapSequence:
      return self.bootstrapSequence.pop()
    elif random.random() < self.trickyProbability and self.tricky:
      return self.getTricky()
    else:
      return self.getNormal()



class Int(WithTrickySet):
  """An arbitrary integer."""

  def __init__(self, low=(-sys.maxint-1), high=sys.maxint):
    """Generate integers between optional low (inclusive) and high (exclusive) bounds."""
    self.low, self.high = int(low), int(high)
    tricky = [x for x in (0, 1, -1, 65536, low, high - 1) if low <= x < high]
    WithTrickySet.__init__(self, tricky)


  def getNormal(self):
    """Get a normal item."""
    return random.randint(self.low, self.high - 1)



class Float(WithTrickySet):
  """An arbitrary float."""

  def __init__(self, low=-10e10, high=10e10):
    """Generate integers between optional low and high bounds. Never yields NaN."""
    self.low, self.high = float(low), float(high)
    tricky = [x for x in (0.0, -0.0, 1.0, -1.0, 1e-10, -1e-10, low, high, FLOAT_EPS) if low <= x <= high]
    WithTrickySet.__init__(self, tricky)


  def getNormal(self):
    """Get a normal item."""
    if random.random() < 0.6:
      return random.triangular(self.low, self.high)
    else:
      return random.uniform(max(self.low, -10.0), min(self.high, 10.0))



class RandomString(WithTrickySet):
  """An arbitrary string of random bytes."""

  def __init__(self):
    self.short, self.long = Int(0, 10), Int(0, 500)
    tricky = ['', '\0', '\xc2', '\0foo']
    WithTrickySet.__init__(self, tricky)


  def getNormal(self):
    """Get a normal item."""
    if random.random() < 0.5:
      return os.urandom(self.short.next())
    else:
      return os.urandom(self.long.next())



class StringFromList(object):
  """Randomly choose strings from list."""

  def __init__(self, strings):
    assert strings, "List of strings %r must not be empty." % strings
    self.strings = list(strings)


  def __iter__(self):
    return self


  def next(self):
    """Return a random string from the list."""
    return random.choice(self.strings)


################################################################################
## DERIVED GENERATORS: This is a much easier way to do it, FYI.
################################################################################

# Some of these "names" are pretty messed up. Such is life in our flawed world.
FULL_NAMES = (
  '', u'\xa0', 'Nile Etland', 'pookie', 'Carson von Mekhan', "Sir Giles o' the Wold",
  'Harry James Potter-Evans-Verres', 'Prince', 'The Artist Formerly Known as Prince',
  'J. R. R. Tolkien', 'Dr Who', 'Dr. Zhivago', 'Rev. Ezekiel Salem Furywright',
  'Richard M. Jones III, Esq.', 'Pete', "Chargin' Chuck", 'Football Charlie',
  '!!!', 'Senor Cardgage', u'Se\xf1nor Cardgage', 'Senhor Cardgage',
  u'Robert (\u256f\xb0\u25a1\xb0\uff09\u256f\ufe35 \u253b\u2501\u253b)', # table flipping
  u'\u5317\u65b9 \u62d3\u8299', u'Bei-Fong Toph (\u5317\u65b9 \u62d3\u8299)',
  u'Scott\x10Pilgrim', u'Black\u2606Star', 'justinbeiberfan69', '^-------@\0woo$',
  "Robert'); DROP TABLE Students;--", "a b c 1 2 3 lol butts lol @ u!!1",
  u'\u2606\u2606 Tom Swift \u2606\u2606', u'\u2606\u2606\u2606\u2606',
  'Rupert "Ripper" Giles', 'Jesse Ramsbotham', 'e^(i*pi) = -1', 'HARRRR',
  u'Robert \U00010308 Smith',      # Decoration from outside the basic multilingual plane
  u'\U00010308 \U00010308 Sleipnir McTavish \U00010308 \U00010308', # Cool name!
  'Bob Dole', 'bob dole', '  bob dole\t', 'Bob\tdole', 'Bob Dole <bdole@bob.co.nz> ',
)


@arbfun('name')
def name():
  """Return names in Unicode."""
  return itertools.cycle(map(unicode, FULL_NAMES))


@arbfun('nameUtf8')
def nameUtf8():
  """Return names in UTF-8."""
  return itertools.cycle(name.encode('utf8') for name in FULL_NAMES)
