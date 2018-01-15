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


class QuadraticPolynomial(bcls.CamberLine):
    angle_of_inflow = fdn.BoundedNumericProperty(lb=0, ub=180)

    def __init__(self, angle_of_inflow):
        super(QuadraticPolynomial, self).__init__()
        self.angle_of_inflow = angle_of_inflow

    @classmethod
    def default(cls):
        return cls(angle_of_inflow=100)

    def _get_coefficients(self):
        a = math.tan(np.deg2rad(self.angle_of_inflow) - math.pi / 2.)
        return a, -a

    @fdn.memoize
    def get_derivations(self):
        x = self.distribution(self.sample_rate)
        a_1, a_2 = self._get_coefficients()
        return x * (x * 2 * a_2) + a_1

    @fdn.memoize
    def as_array(self):
        x = self.distribution(self.sample_rate)
        a_1, a_2 = self._get_coefficients()
        y = x * (x * a_2 + a_1)
        return np.append(x[:, None], y[:, None], axis=1)
