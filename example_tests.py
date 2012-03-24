"""Examples for QuickCheck. Run with nosetests."""

import zlib
import math

import qc

# This test will be run 100 times, with a variety of strings, and we run the function
# each time. Since zlib works, this test should always pass.

@qc.property
def test_compress_decompress():
    """Test that compressing and decompressing gives the original string."""
    data = qc.str()
    assert zlib.decompress(zlib.compress(data)) == data, repr(data)

# Some silly string properties. Again, pretty simple.

@qc.property
def test_upper_lower_utf8():
    data = qc.str()
    assert data.upper().lower() == data.lower().upper().lower(), repr(data)


@qc.property
def test_upper_lower_unicode():
    data = qc.unicode()
    assert data.upper().lower() == data.lower().upper().lower(), repr(data)


# Now let's try testing out something a bit more custom! The point() function will
# generate points with coordinates designed to produce interesting combinations, like the
# ever-popular (0, 0), or stuff like (-1, 0).


class Point(object):
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)


def point():
    """Get an arbitrary point."""
    x = qc.int(-20, 20)
    y = qc.int(-34, 50)
    return Point(x, y)


@qc.property
def test_triangle_inequality():
    """Reference: http://en.wikipedia.org/wiki/Triangle_inequality"""
    pt = point()
    assert abs(pt.x) + abs(pt.y) >= math.sqrt(pt.x**2 + pt.y**2), (pt.x, pt.y)


# It really is that simple!
