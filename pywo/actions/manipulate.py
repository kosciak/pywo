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

    def __init__(self, current, axis, adjacent=True, workarea=None):
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

    def __init__(self, current, direction, inclusive=False, adjacent=True,
                 workarea=None):
        area = in_direction_geometry(current, direction, inclusive, workarea)
        filters.AND.__init__(self,
                             filters.Overlap(workarea),
                             filters.Overlap(area, adjacent))

