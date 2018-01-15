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


class Joukowski(bcls.CamberLine):
    max_camber = fdn.NumericProperty()

    def __init__(self, max_camber):
        super(Joukowski, self).__init__()
        self.max_camber = max_camber

    @classmethod
    def default(cls):
        return cls(max_camber=0.12)

    @fdn.memoize
    def get_derivations(self):
        x = self.distribution(self.sample_rate)
        return self.max_camber * (1 - 2 * x)

    @fdn.memoize
    def as_array(self):
        x = self.distribution(self.sample_rate)
        y = self.max_camber * x * (1 - x)
        return np.append(x[:, None], y[:, None], axis=1)
