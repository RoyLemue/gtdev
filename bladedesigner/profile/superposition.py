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

from . import profile as bcls
from .. import foundation as fdn

from .. import camberline
from .. import thicknessdistribution


class Superposition(bcls.Profile):
    thickness_distribution = fdn.ChildProperty()

    def __init__(self, camber_line, thickness_distribution):
        super(Superposition, self).__init__(camber_line)
        self.thickness_distribution = thickness_distribution
        self.sslp = 50

    @classmethod
    def default(cls):
        camber_line = camberline.NACA2Digits.default()
        thickness_distribution = thicknessdistribution.NACA4Digits.default()
        return cls(camber_line, thickness_distribution)

    @fdn.memoize
    def as_array(self):
        x = self.distribution(self.sample_rate)
        y_c = self.camber_line.as_array().transpose()[1]
        y_t = self.thickness_distribution.as_array().transpose()[1]
        if y_t[-1] != 0:
            if self.sample_rate >= self.sslp:
                x[-2] = 1
                y_c[-2] = y_c[-1]
                y_t[-2], y_t[-1] = y_t[-1], 0
            else:
                y_t[-1] = 0
        theta = np.arctan(self.camber_line.get_derivations())
        sin_theta = np.sin(theta)
        cos_theta = np.cos(theta)
        x_u, x_l = x - y_t * sin_theta, x + y_t * sin_theta
        y_u, y_l = y_c + y_t * cos_theta, y_c - y_t * cos_theta
        x_u, y_u = x_u[::-1], y_u[::-1]
        x = np.append(x_u[:-1], x_l)
        y = np.append(y_u[:-1], y_l)
        return np.append(x[:, None], y[:, None], axis=1)
