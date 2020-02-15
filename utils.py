import sys
from numbers import Number
from collections import Set, deque

zero_depth_bases = (str, bytes, Number, range, bytearray)


def getsize(obj_0):
    """Recursively iterate to sum size of object & members."""

    _seen_ids = set()

    def inner(obj):

        obj_id = id(obj)

        if obj_id in _seen_ids:
            return 0

        _seen_ids.add(obj_id)

        size = sys.getsizeof(obj)

        if isinstance(obj, zero_depth_bases):
            pass

        elif isinstance(obj, (tuple, list, Set, deque)):
            size += sum(inner(i) for i in obj)

        elif isinstance(obj, dict):
            size += sum(inner(k) + inner(v) for k, v in obj.items())

        return size

    return inner(obj_0)
