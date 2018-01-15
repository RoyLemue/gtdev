#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# Copyright (C) 2011-2014 Andreas Kührmann [andreas.kuehrmann@gmail.com]
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
# =============================================================================


import copy
import functools


def memoize(function):
    """
    This decorator caches a method's return value. If it's called later, the
    cached value is returned, and not re-evaluated.

    Example:

    >>> class Foo(object):
    ...
    ...     @memoize
    ...     def complex_computation(self):
    ...         return 0
    """

    @functools.wraps(function)
    def wrapper(obj):
        cache = obj.__dict__.setdefault('cache', dict())
        key = function.__name__
        try:
            return copy.copy(cache[key])
        except KeyError:
            result = cache[key] = function(obj)
            return result

    return wrapper
