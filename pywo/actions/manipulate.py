#
# PyWO - Python Window Organizer
# Copyright 2010, Wojciech 'KosciaK' Pietrzok
#
# This file is part of PyWO.
#
# PyWO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyWO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyWO.  If not, see <http://www.gnu.org/licenses/>.
#

"""manipulate.py - common methods and classes used in windows manipulation."""

import logging
import operator

from pywo.core import WindowManager, Window, Geometry
from pywo.core import filters


__author__ = "Wojciech 'KosciaK' Pietrzok, Aron Griffis"


log = logging.getLogger(__name__)

WM = WindowManager()

ATTRGETTERS = {'x': (operator.attrgetter('x'),
                     operator.attrgetter('x2'),
                     operator.attrgetter('width')),
               'y': (operator.attrgetter('y'),
                     operator.attrgetter('y2'),
                     operator.attrgetter('height'))}


class GeometryWindow(Window, Geometry):

    """Combined Window and it's Geometry.
    
    On some window managers getting correct window geometry require many
    operations. Using this class window geometry is checked only once.
    
    """

    def __init__(self, window):
        Window.__init__(self, window.id)
        geometry = window.geometry
        Geometry.__init__(self, 
                          geometry.x, geometry.y, 
                          geometry.width, geometry.height)

    @property
    def geometry(self):
        return self


def in_axis_geometry(geometry, axis, workarea=None):
    """Return geometry stretched in given axis."""
    workarea = workarea or WM.workarea_geometry
    if axis == 'x':
        return Geometry(geometry.x, workarea.y, geometry.width, workarea.height)
    elif axis == 'y':
        return Geometry(workarea.x, geometry.y, workarea.width, geometry.height)


class InAxis(filters.AND):

    """Return windows placed in x or y axis to current window.

    Return windows for which at least one edge is between right/left or
    top/bottom edge of current window, or current window is between
    current window's edges.

    """

    def __init__(self, current, axis, adjacent=False, workarea=None):
        area = in_axis_geometry(current, axis, workarea)
        filters.AND.__init__(self,
                             filters.Overlap(workarea),
                             filters.Overlap(area, adjacent))


def in_direction_geometry(geometry, direction, inclusive=False, workarea=None):
    """Return geometry in given direction from the given geometry.

    If inclusive is True include given geometry.

    """
    workarea = workarea or WM.workarea_geometry
    if direction.is_middle:
        return workarea

    def in_axis(axis, top_left, bottom_right):
        """Return pair of x/y and width/height."""
        xy, xy2, size = ATTRGETTERS[axis]
        new_xy = xy(workarea)
        new_size = size(workarea)
        if top_left:
            if inclusive:
                new_size = xy2(geometry) - new_xy
            else:
                new_size = xy(geometry) - new_xy
        if bottom_right:
            if inclusive:
                new_xy = xy(geometry)
            else:
                new_xy = xy2(geometry)
            new_size = xy2(workarea) - new_xy
        return new_xy, new_size

    x, width = in_axis('x', direction.is_left, direction.is_right)
    y, height = in_axis('y', direction.is_top, direction.is_bottom)
    return Geometry(x, y, width, height)


class InDirection(filters.AND):

    """Return windows placed in the given direction from the current window.

    Return windows for which at least one edge is beyond the current window in
    the given direction. If inclusive is True, then include windows in current's
    plane.

    """

    def __init__(self, current, direction, inclusive=False, adjacent=False,
                 workarea=None):
        area = in_direction_geometry(current, direction, inclusive, workarea)
        print area
        filters.AND.__init__(self,
                             filters.Overlap(workarea),
                             filters.Overlap(area, adjacent))


class Resizer(object):

    """Abstract Resizer finds new geometry for window.
    
    NOTE: current and others are instances of GeometryWindow, 
          that are subclass of both Window and Geometry
    
    """

    def __init__(self, workarea=None, adjacent=True, vertical_first=True):
        self.workarea = workarea or WM.workarea_geometry
        self.adjacent = adjacent
        self.vertical_first = vertical_first

    def __call__(self, win, direction):
        """Return new geometry for the window."""
        return self.resize(win, direction)

    def resize(self, win, direction):
        """Return new geometry for the window."""
        current = win.geometry & self.workarea
        windows = WM.windows(filters.AND(filters.ExcludeId(win.id),
                                         filters.STANDARD, 
                                         filters.Desktop()))
        others = [GeometryWindow(window) for window in windows]
        axis_order = [['x', 'y'], ['y', 'x']]
        for axis in axis_order[self.vertical_first]:
            current = self.__resize_in_axis(axis, current, others, direction)
        return current

    def __resize_in_axis(self, axis, current, others, direction):
        """Set left and right, or top and bottom edges of new window's position."""
        xy, xy2, size = ATTRGETTERS[axis]
        opposite_axis = ['x', 'y'][axis == 'x']
        size = {'x':'width', 'y':'height'}[axis]
        in_axis_filter = InAxis(current, opposite_axis, self.adjacent, 
                                self.workarea)
        others = filter(in_axis_filter, others)
        if (axis == 'x' and direction.is_left) or \
           (axis == 'y' and direction.is_top):
            new_xy = self.top_left(current, others, axis)
            setattr(current, size, xy2(current) - new_xy)
            setattr(current, axis, new_xy)
        if (axis == 'x' and direction.is_right) or \
           (axis == 'y' and direction.is_bottom):
            new_xy2 = self.bottom_right(current, others, axis)
            setattr(current, size, new_xy2 - xy(current))
        return current

    def top_left(self, current, others, axis):
        """Return top or left edge of new window's position."""
        raise NotImplementedError()

    def bottom_right(self, current, others, axis):
        """Return bottom or right edge of new window's position."""
        raise NotImplementedError()


class Expander(Resizer):

    """Expands window in given direction."""

    def __init__(self, workarea=None, adjacent=True, vertical_first=True, 
                 both_sides=False):
        Resizer.__init__(self, workarea, adjacent, vertical_first)
        self.both_sides = both_sides

    def top_left(self, current, others, axis):
        """Return top or left edge of new window's position."""
        xy, xy2, size = ATTRGETTERS[axis]
        edges = [xy(self.workarea)]
        for other in others:
            if xy2(other) < xy(current) or \
               (not self.adjacent and xy2(other) <= xy(current)):
                edges.append(xy2(other))
            if self.both_sides and \
               xy(self.workarea) < xy(other) < xy(current):
                edges.append(xy(other))
        return max(edges)

    def bottom_right(self, current, others, axis):
        """Return bottom or right edge of new window's position."""
        xy, xy2, size = ATTRGETTERS[axis]
        edges = [xy2(self.workarea)]
        for other in others:
            if xy(other) > xy2(current) or \
               (not self.adjacent and xy(other) >= xy2(current)):
                edges.append(xy(other))
            if self.both_sides and \
               xy2(current) < xy2(other) < xy2(self.workarea):
                edges.append(xy2(other))
        return min(edges)


class Shrinker(Resizer):

    """Shrinks window in given direction."""

    @staticmethod
    def __edges(current, others, axis):
        """Return coordinates of other window edges."""
        xy, xy2, size = ATTRGETTERS[axis]
        edges = []
        for other in others:
            if xy(current) < xy(other) < xy2(current):
                edges.append(xy(other))
            if xy(current) < xy2(other) < xy2(current):
                edges.append(xy2(other))
        return edges

    def top_left(self, current, others, axis):
        """Return top or left edge of new window's position.
        
        Use only coordinates inside current window.
        
        """
        xy, xy2, size = ATTRGETTERS[axis]
        edges = self.__edges(current, others, axis) or [xy(current)]
        return min(edges)

    def bottom_right(self, current, others, axis):
        """Return bottom or right edge of new window's position.
        
        Use only coordinates inside current window.
        
        """
        xy, xy2, size = ATTRGETTERS[axis]
        edges = self.__edges(current, others, axis) or [xy2(current)]
        return max(edges)


class Floater(Expander):

    """Stick to the inside, and outside edge of other windows."""

    def top_left(self, current, others, axis):
        """Return top or left edge of new window's position."""
        xy, xy2, size = ATTRGETTERS[axis]
        edges = [Expander.top_left(self, current, others, axis), ]
        for other in others:
            if not self.adjacent and not self.both_sides:
                break
            if xy(current) <= xy(other) < xy2(current) and \
               xy(other) - size(current) > xy(self.workarea):
                edges.append(xy(other) - size(current))
            if xy(current) <= xy2(other) < xy2(current) and \
               xy2(other) - size(current) > xy(self.workarea):
                edges.append(xy2(other) - size(current))
        return max(edges)

    def bottom_right(self, current, others, axis):
        """Return bottom or right edge of new window's position."""
        xy, xy2, size = ATTRGETTERS[axis]
        edges = [Expander.bottom_right(self, current, others, axis), ]
        for other in others:
            if not self.adjacent and not self.both_sides:
                break
            if xy(current) < xy(other) <= xy2(current) and \
               xy(other) + size(current) < xy2(self.workarea):
                edges.append(xy(other) + size(current))
            if xy(current) < xy2(other) <= xy2(current) and \
               xy2(other) + size(current) < xy2(self.workarea):
                edges.append(xy2(other) + size(current))
        return min(edges)

