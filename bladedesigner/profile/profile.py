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


import math

import numpy as np

from .. import baseclass as bcls
from .. import foundation as fdn

from .. import distribution


class Profile(bcls.TwoDimNode):
    camber_line = fdn.ChildProperty()
    sample_rate = fdn.SharedBoundedNumericProperty(lb=0, ub=9999, default=200)
    distribution = fdn.SharedProperty(default=distribution.Chebyshev())

    def __init__(self, camber_line):
        super(Profile, self).__init__()
        self.camber_line = camber_line
        self.name = 'Profile'

    @property
    def angle_of_inflow(self):
        derivations = self.camber_line.get_derivations()
        return math.atan(derivations[0]) + math.pi * .5

    @property
    def angle_of_outflow(self):
        derivations = self.camber_line.get_derivations()
        return math.atan(derivations[-1]) + math.pi * .5

    @property
    def centroid(self):
        area = 0.
        centroid = np.zeros((2,))
        x, y = self.as_array().transpose()
        for index in np.arange(x.size - 1):
            segment = x[index] * y[index + 1] - x[index + 1] * y[index]
            centroid[0] += (x[index] + x[index + 1]) * segment
            centroid[1] += (y[index] + y[index + 1]) * segment
            area += segment
        return centroid / 3 / abs(area)
