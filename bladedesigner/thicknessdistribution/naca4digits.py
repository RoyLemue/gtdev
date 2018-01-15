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

from . import thicknessdistribution as bcls
from .. import foundation as fdn


class NACA4Digits(bcls.ThicknessDistribution):
    max_thickness = fdn.BoundedNumericProperty(lb=0, ub=9999)

    def __init__(self, max_thickness):
        super(NACA4Digits, self).__init__()
        self.max_thickness = max_thickness

    @classmethod
    def default(cls):
        return cls(max_thickness=0.12)

    @fdn.memoize
    def as_array(self):
        A, B, C, D, E = 1.4845, -0.63, -1.758, 1.4215, -0.5075
        t = self.max_thickness
        x = self.distribution(self.sample_rate)
        y = t * (A * np.sqrt(x) + x * (B + x * (C + x * (D + x * E))))
        return np.append(x[:, None], y[:, None], axis=1)
