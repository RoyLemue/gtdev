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


import numpy as np

from . import node as bcls
from .. import foundation as fdn


class TwoDimNode(bcls.Node):
    color = fdn.MPLProperty(default='k')
    linestyle = fdn.MPLProperty(default='-')
    linewidth = fdn.MPLProperty(default=1)
    marker = fdn.MPLProperty(default='')
    markersize = fdn.MPLProperty(default=5)
    visible = fdn.MPLProperty(default=True)

    def __init__(self):
        super(TwoDimNode, self).__init__()
        self._array_line = None

    @property
    def array_line(self):
        if self._array_line is not None:
            return self._array_line
        reply = fdn.line2D_requested.send(sender=TwoDimNode)
        if reply:
            self._array_line = reply[0][1]
            self._init_line2D(self._array_line)
        return self._array_line

    @array_line.setter
    def array_line(self, array_line):
        if self._array_line is array_line:
            return
        del self.array_line
        self._array_line = array_line
        self._init_line2D(array_line)

    @array_line.deleter
    def array_line(self):
        if self._array_line is None:
            return None
        self._array_line.remove()
        if self.auto_draw:
            self.draw_on_canvas()
        self._array_line = None

    def _init_line2D(self, line2D):
        for p in self.properties:
            if isinstance(p, fdn.MPLProperty):
                getattr(line2D, 'set_{}'.format(p.name))(p.get(self))

    def prepare_to_draw(self):
        data = np.array(self.array_line.get_data())
        if data.size:
            return None
        x, y = self.as_array().transpose()
        self.array_line.set_data(x, y)

    def draw_on_canvas(self):
        self.array_line.figure.canvas.draw()

    def update(self, broadcast=True):
        if self.__dict__.pop('cache', None) is None:
            return None
        if self.array_line is not None:
            self.array_line.set_data(np.array([]), np.array([]))
            if self.visible and self.auto_draw:
                self.prepare_to_draw()
                self.draw_on_canvas()
        if broadcast:
            self.observers.notify()
