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


class QuarticPolynomial(bcls.CamberLine):
    angle_of_inflow = fdn.BoundedNumericProperty(lb=0, ub=180)
    angle_of_outflow = fdn.BoundedNumericProperty(lb=0, ub=180)
    max_camber_position = fdn.BoundedNumericProperty(lb=0, ub=1)

    def __init__(self, angle_of_inflow, angle_of_outflow, max_camber_position):
        super(QuarticPolynomial, self).__init__()
        self.angle_of_inflow = angle_of_inflow
        self.angle_of_outflow = angle_of_outflow
        self.max_camber_position = max_camber_position

    @classmethod
    def default(cls):
        angle_of_inflow = 100
        angle_of_outflow = 90
        max_camber_position = 0.4
        return cls(angle_of_inflow, angle_of_outflow, max_camber_position)

    def _get_coefficients(self):
        slope_inlet = math.tan(np.deg2rad(self.angle_of_inflow) - np.pi / 2.)
        slope_outlet = math.tan(np.pi / 2. - np.deg2rad(self.angle_of_outflow))
        p = self.max_camber_position
        a_4 = (((p * (4 - 3 * p) - 1) * slope_inlet + p * (3 * p - 2)
                * slope_outlet) / (2 * p * (2 * p) * (p - 1)))
        a_3 = slope_inlet - slope_outlet - 2 * a_4
        a_2 = -slope_inlet - a_3 - a_4
        a_1 = slope_inlet
        return a_1, a_2, a_3, a_4

    @fdn.memoize
    def get_derivations(self):
        x = self.distribution(self.sample_rate)
        a_1, a_2, a_3, a_4 = self._get_coefficients()
        return x * (x * (4 * a_4 * x + 3 * a_3) + 2 * a_2) + a_1

    @fdn.memoize
    def as_array(self):
        x = self.distribution(self.sample_rate)
        a_1, a_2, a_3, a_4 = self._get_coefficients()
        y = x * (x * (x * (a_4 * x + a_3) + a_2) + a_1)
        return np.append(x[:, None], y[:, None], axis=1)
