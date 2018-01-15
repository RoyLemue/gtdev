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

from . import camberline as bcls
from .. import foundation as fdn


class CircularArc(bcls.CamberLine):
    angle_of_inflow = fdn.BoundedNumericProperty(lb=0, ub=180)

    def __init__(self, angle_of_inflow):
        super(CircularArc, self).__init__()
        self.angle_of_inflow = angle_of_inflow

    @classmethod
    def default(cls):
        return cls(angle_of_inflow=100)

    @fdn.memoize
    def get_derivations(self):
        chi = self.angle_of_inflow
        sign = 1 if chi < 90 else -1
        r2 = (.5 / math.cos(np.deg2rad(chi))) ** 2
        x = self.distribution(self.sample_rate) - .5
        return sign * x / np.sqrt(r2 - x ** 2)

    @fdn.memoize
    def as_array(self):
        chi = self.angle_of_inflow
        sign = -1 if chi < 90 else 1
        r2 = (.5 / math.cos(np.deg2rad(chi))) ** 2
        x = self.distribution(self.sample_rate)
        y = sign * (np.sqrt(r2 - (x - .5) ** 2) - np.sqrt(r2 - .25))
        return np.append(x[:, None], y[:, None], axis=1)
