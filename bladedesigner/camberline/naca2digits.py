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


import numpy as np

from . import camberline as bcls
from .. import foundation as fdn


class NACA2Digits(bcls.CamberLine):
    max_camber = fdn.NumericProperty()
    max_camber_position = fdn.BoundedNumericProperty(lb=0, ub=1)

    def __init__(self, max_camber, max_camber_position):
        super(NACA2Digits, self).__init__()
        self.max_camber = max_camber
        self.max_camber_position = max_camber_position

    @classmethod
    def default(cls):
        return cls(max_camber=0.02, max_camber_position=0.4)

    @fdn.memoize
    def get_derivations(self):
        p = self.max_camber_position
        m = self.max_camber
        x = self.distribution(self.sample_rate)
        index = np.where(x <= p)[0]
        if index.size:
            dydx_1 = 2 * m / np.power(p, 2) * (p - x[index])
        index = np.where(x > p)[0]
        if index.size:
            dydx_2 = m / (1 - p) ** 2 * 2 * (p - x[index])
        return np.append(dydx_1, dydx_2)

    @fdn.memoize
    def as_array(self):
        p = self.max_camber_position
        m = self.max_camber
        x = self.distribution(self.sample_rate)
        index = np.where(x <= p)[0]
        if index.size:
            z = x[index]
            y1 = m / p ** 2 * (z * (2 * p - z))
        index = np.where(x > p)[0]
        if index.size:
            z = x[index]
            y2 = m / (1 - p) ** 2 * (1 - 2 * p + z * (2 * p - z))
        y = np.append(y1, y2)
        return np.append(x[:, None], y[:, None], axis=1)
