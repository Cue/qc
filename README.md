QuickCheck: randomized testing made trivial
===========

QuickCheck is a style of testing where you write *properties* that you expect to hold,
and let the computer generate randomized test cases to check that these properties
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
        data = qc.string()                  # An arbitrary string. Values are randomized.
        self.assertEquals(data, decompress(compress(data)))
```

That's an ordinary test with Python's built-in unittest framework. Alternately, you could
do the exact same thing with a different testing framework, like
[nose](http://readthedocs.org/docs/nose/en/latest/). The `@qc.property` decorator runs
the decorated function several times, and each time the values returned by functions like
`qc.string()` are different. In other words, qc is compatible with pretty much every unit
test framework out there; it's not particularly demanding.

Functions like `qc.string()`, `qc.int()`, and so on, generate arbitrary values of a
certain type. In the example above, we're asserting that the property holds true for all
strings. When you run the tests, qc will generate randomized strings for testing.

You'll notice that I said "randomized", not "random". This is intentional. The
distribution of values is tweaked to include interesting values, like empty strings, or
strings with NUL characters in the middle, or strings containing English text. In
general, qc tries to give a good mix of clever tricky values and randomness. This is
essentially what you would do, if you had to write really thorough test cases by hand,
except that you don't have to do it. Also, the computer has fewer preconceptions about
what constitutes sane data, so it will often find bugs that would never have occurred to
you to write test cases for. It doesn't know how to subconsciously avoid the bugs.

You're not limited to the built-in arbitrary value functions. You can use them as
building blocks to generate your own. For example:

```python
class Point(object):
    def __init(self, x, y):
        self.x, self.y = x, y

def point():
    """Get an arbitrary point."""
    return Point(qc.int(), qc.int())
```

You can then use this to generate arbitrary point values in properties:

```python
@qc.property
def test_triangle_inequality(self):
    pt = point()
    self.assertTrue(pt.x + pt.y >= math.sqrt(pt.x**2 + pt.y**2))
```

When you run this, something magical happens: qc will try to generate tricky values for
both the x and y variables in the `Point` class, *together*, so you'll see points like
(0, 0), (1, 1), (0, 1), (385904, 0), as well as totally random ones like (584,
-35809648). In other words, rather than just drawing x and y values from a stream of
random numbers with some tricky values in it, qc will actually try to generate tricky (x,
y) tuples.
