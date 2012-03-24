# -*- coding: utf-8 -*-

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

  def __init__(self, maxlen=sys.maxint):
    self.short, self.long = Int(0, min(maxlen, 10)), Int(0, min(maxlen, 500))
    tricky = ['', '\0', '\xc2', '\0foo']
    WithTrickySet.__init__(self, tricky)


  def getNormal(self):
    """Get a normal item."""
    if random.random() < 0.5:
      return os.urandom(self.short.next())
    else:
      return os.urandom(self.long.next())


################################################################################
## DERIVED GENERATORS: The @arbfun decorator is like an angel of concision.
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
  u'Robert \U00010308 Smith', # Decoration from outside the basic multilingual plane. O_O
  u'\U00010308 \U00010308 Sleipnir McTavish \U00010308 \U00010308', # Cool name!
  'Bob Dole :-)', 'bob dole', '  bob dole\t', 'Bob\tdole', 'Bob Dole <bdole@bob.co.nz> ',
)


@arbfun
def name():
  """Return names in Unicode."""
  return itertools.cycle(map(unicode, FULL_NAMES))


@arbfun
def nameUtf8():
  """Return names in UTF-8."""
  return itertools.cycle(name.encode('utf8') for name in FULL_NAMES)


@arbfun
def fromList(items):
  """Randomly choose items from list."""
  assert items, "List of items %r must not be empty." % items
  while True:
    return random.choice(items)


################################################################################
## STRINGS: These are important, so let's put some effort into perversity.
################################################################################

# This pleases me considerably more than lorem ipsum.
AENEID_PRELUDE = """
Arms, and the man I sing, who, forc'd by fate,
And haughty Juno's unrelenting hate,
Expell'd and exil'd, left the Trojan shore.
Long labors, both by sea and land, he bore,
And in the doubtful war, before he won
The Latian realm, and built the destin'd town;
His banish'd gods restor'd to rites divine,
And settled sure succession in his line,
From whence the race of Alban fathers come,
And the long glories of majestic Rome.

O Muse! the causes and the crimes relate;
What goddess was provok'd, and whence her hate;
For what offense the Queen of Heav'n began
To persecute so brave, so just a man;
Involv'd his anxious life in endless cares,
Expos'd to wants, and hurried into wars!
Can heav'nly minds such high resentment show,
Or exercise their spite in human woe?"""

# A thoroughly out-of-copyright poem by Fujiwara no Teika
JAPANESE_POEM = u"こぬ人を\nまつほの浦の\n夕なぎに\n焼くやもしほの\n身もこがれつつ"

# Neitzsche telling people that he's SO VERY SERIOUS. In German.
NEITZSCHE_BLUSTER = u"""In Voraussicht, dass ich über Kurzem mit der schwersten Forderung
an die Menschheit herantreten muss, die je an sie gestellt wurde,
scheint es mir unerlässlich, zu sagen, wer ich bin. Im Grunde dürfte
man's wissen: denn ich habe mich nicht "unbezeugt gelassen". Das
Missverhältniss aber zwischen der Grösse meiner Aufgabe und der
Kleinheit meiner Zeitgenossen ist darin zum Ausdruck gekommen, dass
man mich weder gehört, noch auch nur gesehn hat. Ich lebe auf meinen
eignen Credit hin, es ist vielleicht bloss ein Vorurtheil, dass ich
lebe?... Ich brauche nur irgend einen "Gebildeten" zu sprechen, der im
Sommer ins Oberengadin kommt, um mich zu überzeugen, dass ich nicht
lebe... Unter diesen Umständen giebt es eine Pflicht, gegen die
im Grunde meine Gewohnheit, noch mehr der Stolz meiner Instinkte
revoltirt, nämlich zu sagen: Hört mich! denn ich bin der und der.
Verwechselt mich vor Allem nicht!"""

# Mostly unattributed quotes. Google will provide the attribution. pylint: disable=C0301
QUOTES = [
  "I don't want to achieve immortality through my work. I want to achieve it through not dying.",
  "Copper, 40g; Zinc, 25g; Nickel, 15g; Hiding Embarrassment, 5g. Spite, 97kg.",
  "In a hole in the ground there lived a hobbit.",
  u"I just bought a 2-bedroom house, but it's up to me, isn't it, how many bedrooms there are? Fuck you, real estate lady! This bedroom has a oven in it! This bedroom’s got a lot of people sitting around watching TV. This bedroom is A.K.A. a hallway.",
  "Hello, world!"
  "As an adolescent I aspired to lasting fame, I craved factual certainty, and I thirsted for a meaningful vision of human life - so I became a scientist. This is like becoming an archbishop so you can meet girls.",
  "As we know, There are known knowns. There are things we know we know. We also know there are known unknowns. That is to say, we know there are some things we do not know. But there are also unknown unknowns, the ones we don't know we don't know.",
]


# A bunch of words or word-like strings, for when you need words.
WORDS = sorted(set(AENEID_PRELUDE.split() + JAPANESE_POEM.split() + NEITZSCHE_BLUSTER.split()))


def shortstr():
  """Return a short string."""
  return ' '.join([random.choice(WORDS) for _ in xrange(random.randint(0, 10))])


def longstr():
  """Return a long string."""
  r = random.random()
  if r < 0.2:
    return random.choice((AENEID_PRELUDE, JAPANESE_POEM, NEITZSCHE_BLUSTER))
  elif r < 0.9:
    return random.choice(QUOTES)
  else:
    return shortstr() + AENEID_PRELUDE*20 + '\0' + NEITZSCHE_BLUSTER*10 + shortstr()
