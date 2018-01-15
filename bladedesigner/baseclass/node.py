#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# Copyright (C) 2013-2014 Andreas Kührmann [andreas.kuehrmann@gmail.com]
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


from . import bdobject as bcls
from .. import foundation as fdn

__all__ = ['Node']


def clsname(obj):
    return type(obj).__name__


class Node(bcls.BDObject):
    name = fdn.StringProperty()

    def __init__(self):
        self._parent = None
        self.auto_draw = False
        self.children = fdn.ChildrenList(parent=self)
        self.observers = fdn.ObserverSet()

    @property
    def idx(self):
        if self.parent is None:
            return None
        return self.parent.children.index(self)

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        if not isinstance(parent, Node):
            msg = '{0}.parent accepts only Node objects (got {1})'
            raise ValueError(msg.format(clsname(self), clsname(parent)))
        del self.parent
        self.observers.add(parent)
        self._parent = parent

    @parent.deleter
    def parent(self):
        if self._parent is None:
            return None
        self.observers.remove(self._parent)
        self._parent = None

    def update(self, broadcast=True):
        pass
