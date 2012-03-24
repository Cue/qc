QuickCheck: randomized testing made trivial
===========

QuickCheck is a testing tool that lets you write *properties* that you expect to hold
true, and let the computer generate randomized test cases to check that these properties
actually hold. For example, if you have written `compress` and `decompress` functions for
some data compression program, an obvious property to test is that compressing and
decompressing a string gives back the original string. Here's how you could express that:

```python
import unittest
import qc

class TestCompression(unittest.TestCase):
    @qc.property
    def test_compress_decompress(self):
        """Test that compressing and decompressing returns the original data."""
        data = qc.str()                  # An arbitrary string. Values are randomized.
        self.assertEqual(data, decompress(compress(data)), repr(data))
```

That's an ordinary test with Python's built-in unittest framework (which is why there's
so much boilerplate). Alternately, you could do the exact same thing with a different
testing framework, like the minimally verbose, quite pleasant
[nose](http://readthedocs.org/docs/nose/en/latest/). The `@qc.property` decorator runs
the decorated function several times, and each time the values returned by functions like
`qc.string()` are different. In other words, QuickCheck is compatible with pretty much
every unit test framework out there; it's not particularly demanding.

Functions like `qc.str()`, `qc.int()`, and so on, generate arbitrary values of a
certain type. In the example above, we're asserting that the property holds true for all
strings. When you run the tests, QuickCheck will generate randomized strings for testing.

You'll notice that I said "randomized", not "random". This is intentional. The
distribution of values is tweaked to include interesting values, like empty strings, or
strings with NUL characters in the middle, or strings containing English text. In
general, QuickCheck tries to give a good mix of clever tricky values and randomness. This
is essentially what you would do, if you had to write really thorough test cases by hand,
except that you don't have to do it. In practice, the computer has fewer preconceptions
about what constitutes sane data, so it will often find bugs that would never have
occurred to you to write test cases for. It doesn't know how to subconsciously avoid the
bugs.

You're not limited to the built-in arbitrary value functions. You can use them as
building blocks to generate your own. For example:

```python
class Point(object):
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)

def point():
    """Get an arbitrary point."""
    x = qc.int(-20, 20)
    y = qc.int(-34, 50)
    return Point(x, y)
```

You can then use this to generate arbitrary point values in properties. Here's a
nose-style test:

```python
@qc.property
def test_triangle_inequality():
    pt = point()
    assert abs(pt.x) + abs(pt.y) >= math.sqrt(pt.x**2 + pt.y**2), (pt.x, pt.y)
```

When you run this, something magical happens: QuickCheck will try to generate tricky
values for both the x and y variables in the `Point` class, *together*, so you'll see
points like (0, 0), (1, 1), (0, 1), (385904, 0), as well as totally random ones like
(584, -35809648). In other words, rather than just drawing x and y values from a stream
of random numbers with some tricky values in it, QuickCheck will actually try to generate
tricky combinations of x and y coordinates.

Functions for getting arbitrary data
-------------

* `int(low, high)` gives ints, between the optional bounds `low` and `high`.

* `long(low, high)` gives longs, between the optional bounds `low` and `high`.

* `float(low, high)` gives floats, between the optional bounds `low` and `high`. No
  Infinities or NaN values.

* `str(length=None, maxlen=None)` gives strings, of type `str`. The encoding is UTF-8. If `length` is
  given, the strings will be exactly that long. If `maxlen` is given, the string length
  will be at most `maxlen` characters.

* `unicode(length=None, maxlen=None)` gives unicode strings, of type `unicode`. If
  `length` is given, the strings will be exactly that long. If `maxlen` is given, the
  string length will be at most `maxlen` characters.

* `name()` gives names, in Unicode. These range from the prosaic, like "John Smith", to
  the exotic -- names containing non-breaking spaces, or email addresses, or Unicode
  characters outside the Basic Multilingual Plane. This is, if anything, less perverse
  than the names you will see in a sufficiently large set of Internet data.

* `nameUtf8()` is the same as `name().encode('utf8')`.

* `fromList(items)` returns random items from a list. This is mostly useful for creating
  your own arbitrary data generator functions.

* `randstr(length=None, maxlen=sys.maxint)` gives strings of random bytes. If `length` is
  given, the strings will be exactly that long. If `maxlen` is given, the string length
  will be at most `maxlen` bytes.

The strings produced by `str` and `unicode` are randomized, but some effort has been put
into making them sufficiently perverse as to reveal bugs in a whole lot of string
processing code. The name list is loosely based on horrible memories of seeing name
processing code crash on real-world data, over and over and over again, as it became ever
more clear that the world is mad, and we are truly doomed. (This feeling passes once you
get enough test coverage and things finally stop crashing. There is hope!)

The name and string example data in `qc.arbitrary` may be interesting as a source of more
deteministic test case data. Feel free to borrow any of it. The internals are magic, but
of the magical internal parts, the most interesting ones are in `qc.arbitrary` and `qc`.
