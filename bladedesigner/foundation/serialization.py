#!/usr/bin/env python
# -*- coding: utf-8 -*-


# =============================================================================
# Copyright (C) 2011-2014 Andreas Kührmann [andreas.kuehrmann@gmail.com]
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


import importlib
import json

from . import undo


def serialize_instance(obj):
    d = {'__name__': obj.__class__.__name__,
         '__module__': obj.__class__.__module__}
    d.update({p.name: p.get(obj) for p in obj.properties})
    return d


def unserialize_object(d):
    name = d.pop('__name__', None)
    module = d.pop('__module__', None)
    if name is not None and module is not None:
        cls = getattr(importlib.import_module(module), name)
        obj = cls.default() if hasattr(cls, 'default') else cls()
        for key, value in d.items():
            setattr(obj, key, value)
        return obj
    else:
        return d


def load(filename):
    with open(filename, 'rt') as fp:
        obj = json.load(fp, object_hook=unserialize_object)
    undo.stack().clear()
    return obj


def save(obj, filename):
    with open(filename, 'wt') as fp:
        json.dump(obj, fp, default=serialize_instance, indent=4)
