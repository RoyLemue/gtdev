#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# Copyright (C) 2014 Andreas Kührmann [andreas.kuehrmann@gmail.com]
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


import collections
import re

from .. import foundation as fdn


def convert(string):
    string = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', string)
    string = re.sub('(.)([0-9]+)', r'\1 \2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1 \2', string)


class BDObjectMeta(type):
    @classmethod
    def __prepare__(cls, clsname, bases):
        return collections.OrderedDict()

    def __new__(cls, clsname, bases, clsdict):
        for key, value in clsdict.items():
            if isinstance(value, fdn.Property):
                clsdict[key].name = key
        clsdict = dict(clsdict)
        return super(BDObjectMeta, cls).__new__(cls, clsname, bases, clsdict)

    def __str__(self):
        return convert(self.__name__)


class BDObject(object):
    __metaclass__ = BDObjectMeta

    def __str__(self):
        return convert(type(self).__name__)

    @property
    def properties(self):
        for cls in type(self).__mro__:
            for value in vars(cls).itervalues():
                if isinstance(value, fdn.Property):
                    yield value
