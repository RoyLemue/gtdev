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


from .. import baseclass as bcls
from .. import distribution
from .. import foundation as fdn


class CamberLine(bcls.TwoDimNode):
    sample_rate = fdn.SharedBoundedNumericProperty(lb=0, ub=9999, default=200)
    distribution = fdn.SharedProperty(default=distribution.Chebyshev())

    def __init__(self):
        super(CamberLine, self).__init__()
        self.name = 'Camber Line'

    def get_derivations(self):
        raise NotImplementedError

    def as_array(self):
        raise NotImplementedError
