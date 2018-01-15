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


from .contextmanager import ignored
from .signals import property_changed
from .undo import undoable

name_to_idx = {'camber_line': 0,
               'thickness_distribution': 1,
               }


class Property(object):
    def __init__(self, default=None):
        self.default = default
        self.name = None

    def __get__(self, instance, cls):
        if instance is None:
            return self
        return self.get(instance)

    def __set__(self, instance, new_val):
        self.check(instance, new_val)
        old_val = self.get(instance)
        if new_val == old_val:
            return
        if old_val is not None:
            self.set(instance, new_val, old_val)
        else:
            self._set(instance, new_val, broadcast=False)

    def __delete__(self, instance):
        raise AttributeError("Can't delete")

    def get(self, instance):
        return instance.__dict__.get(self.name, self.default)

    @undoable
    def set(self, instance, new_val, old_val):
        self.will_redo(instance, new_val, old_val)
        self._set(instance, new_val)
        property_changed.send(sender=self, node=instance, value=new_val)
        yield '{} change'.format(self.name)
        self.will_undo(instance, new_val, old_val)
        self._set(instance, old_val)
        property_changed.send(sender=self, node=instance, value=old_val)

    def _set(self, instance, val, broadcast=True):
        instance.__dict__[self.name] = val
        instance.update(broadcast)

    def check(self, instance, val):
        pass

    def will_undo(self, instance, new_val, old_val):
        pass

    def will_redo(self, instance, new_val, old_val):
        pass


class SharedProperty(Property):
    def _set(self, instance, new_val, broadcast=True):
        for child in instance.children:
            descriptor = getattr(type(child), self.name)
            descriptor._set(child, new_val, broadcast=False)
        super(SharedProperty, self)._set(instance, new_val, broadcast)


class NumericProperty(Property):
    def __init__(self, default=0):
        super(NumericProperty, self).__init__(default)

    def check(self, instance, val):
        if not isinstance(val, (int, float, long)):
            raise ValueError('%s.%s accepts only int/float/long (got %s)' % (
                type(instance).__name__, self.name, type(val).__name__))


class SharedNumericProperty(SharedProperty, NumericProperty):
    pass


class BoundedNumericProperty(NumericProperty):
    def __init__(self, lb, ub, default=0):
        super(BoundedNumericProperty, self).__init__(default)
        self.lb = lb
        self.ub = ub

    def check(self, instance, val):
        super(BoundedNumericProperty, self).check(instance, val)
        if val < self.lb:
            raise ValueError('%s.%s is below the lower bound (%f)' % (
                type(instance).__name__, self.name, self.lb))
        if val > self.ub:
            raise ValueError('%s.%s is above the upper bound (%d)' % (
                type(instance).__name__, self.name, self.ub))


class SharedBoundedNumericProperty(SharedProperty, BoundedNumericProperty):
    pass


class StringProperty(Property):
    def __init__(self, default=''):
        super(StringProperty, self).__init__(default)

    def check(self, instance, val):
        if not isinstance(val, (str, unicode)):
            raise TypeError('%s.%s accepts only str/unicode (got %s)' % (
                type(instance).__name__, self.name, type(val).__name__))


class ChildProperty(Property):
    def get(self, instance):
        try:
            return instance.children[name_to_idx[self.name]]
        except IndexError:
            return self.default

    def _set(self, instance, val, broadcast=True):
        for p in val.properties:
            if not isinstance(p, SharedProperty):
                continue
            p._set(val, getattr(instance, p.name), broadcast=False)
        if val.visible and val.auto_draw:
            val.prepare_to_draw()
            val.draw_on_canvas()
        try:
            instance.children[name_to_idx[self.name]] = val
        except IndexError:
            instance.children.append(val)
        instance.update(broadcast)

    def will_redo(self, instance, new_val, old_val):
        getattr(type(new_val), 'visible')._set(new_val, old_val.visible)
        getattr(type(old_val), 'visible')._set(old_val, False)

    def will_undo(self, instance, new_val, old_val):
        getattr(type(old_val), 'visible')._set(old_val, new_val.visible)
        getattr(type(new_val), 'visible')._set(new_val, False)


class MPLProperty(Property):
    def __set__(self, instance, new_val):
        old_val = self.get(instance)
        if new_val == old_val:
            return
        self.set(instance, new_val, old_val)

    def _set(self, instance, val, broadcast=False):
        with ignored(AttributeError):
            getattr(instance.array_line, 'set_{}'.format(self.name))(val)
        instance.__dict__[self.name] = val
        if instance.auto_draw and instance.array_line:
            instance.prepare_to_draw()
            instance.draw_on_canvas()
