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


import collections


def hascallableattr(obj, name):
    return hasattr(obj, name) and callable(getattr(obj, name))


class ChildrenList(collections.MutableSequence):
    def __init__(self, parent):
        self._children = list()
        self._parent = parent

    def __delitem__(self, index):
        del self._children[index]

    def __getitem__(self, index):
        return self._children[index]

    def __setitem__(self, index, item):
        if item.parent:
            raise Exception
        del self._children[index].parent
        item.parent = self._parent
        self._children[index] = item

    def __len__(self):
        return len(self._children)

    def __repr__(self):
        return repr(self._children)

    def __str__(self):
        return str(self._children)

    def insert(self, index, item):
        if item.parent:
            raise Exception
        item.parent = self._parent
        self._children.insert(index, item)


class ObserverSet(collections.MutableSet):
    def __init__(self):
        super(ObserverSet, self).__init__()
        self._observers = set()

    def __contains__(self, element):
        return element in self._observers

    def __iter__(self):
        return iter(self._observers)

    def __len__(self):
        return len(self._observers)

    def __repr__(self):
        return repr(self._observers)

    def __str__(self):
        return str(self._observers)

    def add(self, value):
        if not hascallableattr(value, 'update'):
            msg = "'{0}' object has no callable attribute 'update'"
            raise TypeError(msg.format(type(value).__name__))
        self._observers.add(value)

    def discard(self, value):
        self._observers.discard(value)

    def notify(self):
        map(lambda observer: observer.update(), self._observers)
