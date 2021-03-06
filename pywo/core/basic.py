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

"""Objects representing most basic PyWO concepts."""

import logging
import re


__author__ = "Wojciech 'KosciaK' Pietrzok, Antti Kaihola"


log = logging.getLogger(__name__)


class CustomTuple(tuple):

    """`Tuple` that allows both ``x in [x, y]`` and ``[x,z] in [x, y, z]``"""

    def __contains__(self, item):
        if hasattr(item, '__len__'):
            return set(item) <= set(self)
        return tuple.__contains__(self, item)


class Gravity(object):

    """Gravity point as a percentage of width and height of the :class:`Geometry`."""

    # Predefined gravities, that can be used in config files
    __GRAVITIES = {}
    for xy, names in {
        (0, 0): ['TOP_LEFT', 'UP_LEFT', 'TL', 'UL', 'NW'],
        (0.5, 0): ['TOP', 'UP', 'T', 'U', 'N'],
        (1, 0): ['TOP_RIGHT', 'UP_RIGHT', 'TR', 'UR', 'NE'],
        (0, 0.5): ['LEFT', 'L', 'W'],
        (0.5, 0.5): ['MIDDLE', 'CENTER', 'M', 'C', 'NSEW', 'NSWE'],
        (1, 0.5): ['RIGHT', 'R', 'E'],
        (0, 1): ['BOTTOM_LEFT', 'DOWN_LEFT', 'BL', 'DL', 'SW'],
        (0.5, 1): ['BOTTOM', 'DOWN', 'B', 'D', 'S'],
        (1, 1): ['BOTTOM_RIGHT', 'DOWN_RIGHT', 'BR', 'DR', 'SE'],
    }.items():
        for name in names:
            __GRAVITIES[name] = xy

    def __init__(self, x, y):
        """
        `x`
          is percentage of width
        `y`
          is percentage of height
        """
        self.x = x
        self.y = y
        self.is_middle = (x == 1.0/2) and (y == 1.0/2)
        # FIXME: should is_middle be also is_diagonal?
        self.is_diagonal = (not x == 1.0/2) and (not y == 1.0/2)

    @property
    def is_top(self):
        """Return ``True`` if gravity is toward top."""
        return self.y < 1.0/2 or self.is_middle

    @property
    def is_bottom(self):
        """Return ``True`` if gravity is toward bottom."""
        return self.y > 1.0/2 or self.is_middle

    @property
    def is_left(self):
        """Return ``True`` if gravity is toward left."""
        return self.x < 1.0/2 or self.is_middle

    @property
    def is_right(self):
        """Return ``True`` if gravity is toward right."""
        return self.x > 1.0/2 or self.is_middle

    def invert(self, vertical=True, horizontal=True):
        """Invert the gravity (left becomes right, top becomes bottom)."""
        x, y = self.x, self.y
        if vertical:
            y = 1.0 - self.y
        if horizontal:
            x = 1.0 - self.x
        return Gravity(x, y)

    @staticmethod
    def parse(gravity):
        """Parse gravity string and return :class:`Gravity` object.

        It can be one of predefined __GRAVITIES, or x and y values (floating
        numbers or those described in __SIZES).

        """
        if not gravity:
            return None
        if gravity in Gravity.__GRAVITIES:
            x, y = Gravity.__GRAVITIES[gravity]
            return Gravity(x, y)
        else:
            x, y = [Size.parse_value(xy) for xy in gravity.split(',')]
        return Gravity(x, y)

    def __eq__(self, other):
        return ((self.x, self.y) ==
                (other.x, other.y))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<Gravity x=%.2f, y=%.2f>' % (self.x, self.y)


class Size(object):

    """Encapsulates width and height of the object."""

    # Pattern matching simple calculations with floating numbers
    __PATTERN = re.compile('^[ 0-9\.\+-/\*]+$')

    # Predefined sizes that can be used in config files
    __SIZES = {'FULL': '1.0',
               'HALF': '0.5',
               'THIRD': '1.0/3',
               'QUARTER': '0.25', }
    __SIZES_SHORT = {'F': '1.0',
                     'H': '0.5',
                     'T': '1.0/3',
                     'Q': '0.25', }

    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        """Calculate the area of a rectangle of this size."""
        if isinstance(self.width, list) or isinstance(self.height, list):
            raise ValueError("%s.area doesn't support multiple dimensions: %s"
                             % (self.__class__.__name__, self))
        return self.width * self.height

    @classmethod
    def parse_value(cls, size_string):
        """Parse string representing width or height.

        It can be one of the predefined values, float, or expression.
        If you want to parse list of values separte them with comma.

        """
        if not size_string.strip():
            return None
        size = size_string
        for name, value in cls.__SIZES.items():
            size = size.replace(name, value)
        for name, value in cls.__SIZES_SHORT.items():
            size = size.replace(name, value)
        size = [eval(value) for value in size.split(',')
                            if value.strip() and \
                            cls.__PATTERN.match(value)]
        if size == []:
            raise ValueError('Can\'t parse: %s' % (size_string))
        if len(size) == 1:
            return size[0]
        return size
    
    @staticmethod
    def parse(width, height):
        """Parse width and height strings.
        
        Check :meth:`parse_value` for details.
        
        """
        width = Size.parse_value(width)
        height = Size.parse_value(height)
        if width is not None and height is not None:
            return Size(width, height)
        return None

    def __eq__(self, other):
        return ((self.width, self.height) == (other.width, other.height))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<Size width=%s, height=%s>' % (self.width, self.height)


class Position(object):

    """Encapsulates coordinates of the object.

    Position coordinates starts at top-left corner of the desktop.

    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    # TODO: add parse for relative and absolute values

    def __eq__(self, other):
        return ((self.x, self.y) == (other.x, other.y))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<Position x=%s, y=%s>' % (self.x, self.y)


class Geometry(Position, Size):

    """Combines :class:`Size` and :class:`Position` of the object.

    Position coordinates (x, y) starts at top left corner of the desktop.
    (x2, y2) are the coordinates of the bottom-right corner of the object.

    """

    # TODO: Geometry + Size, Geometry + Position, Geometry * Size

    __DEFAULT_GRAVITY = Gravity(0, 0)

    def __init__(self, x, y, width, height,
                 gravity=__DEFAULT_GRAVITY):
        Size.__init__(self, int(width), int(height))
        Position.__init__(self, int(x), int(y))
        self.set_position(x, y, gravity)

    @property
    def x2(self):
        """X coordinate of bottom right corner."""
        return self.x + self.width

    @property
    def y2(self):
        """Y coordinate of bottom right corner."""
        return self.y + self.height

    def set_position(self, x, y, gravity=__DEFAULT_GRAVITY):
        """Set position with (x,y) as gravity point."""
        # FIXME: why x,y not position?
        self.x = int(x - self.width * gravity.x)
        self.y = int(y - self.height * gravity.y)

    # TODO: def set_size(self, size, gravity)
    #       int() !!!

    def __and__(self, other):
        """Return the intersection with another ``Geometry``.

        Returns ``None`` if the geometries don't intersect. 
        Returns a ``Geometry`` with a zero width and/or height 
        if the geometries touch each other but don't intersect.

        """
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        width = min(self.x2, other.x2) - x
        height = min(self.y2, other.y2) - y
        if width >= 0 and height >= 0:
            return Geometry(x, y, width, height)
        else:
            return None
    
    def __eq__(self, other):
        # NOTE: need to check type(other) for position == geometry,
        #       and size == geometry to work correctly
        if type(other) == Size:
            return Size.__eq__(self, other)
        if type(other) == Position:
            return Position.__eq__(self, other)
        return ((self.x, self.y, self.width, self.height) ==
                (other.x, other.y, other.width, other.height))

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return '<Geometry x=%s, y=%s, width=%s, height=%s, x2=%s, y2=%s>' % \
               (self.x, self.y, self.width, self.height, self.x2, self.y2)


class Extents(object):

    """Encapsulates :class:`~pywo.core.windows.Window` extents (decorations)."""

    def __init__(self, left, right, top, bottom):
        self.top = top or 0
        self.bottom = bottom or 0
        self.left = left or 0
        self.right = right or 0
        if left is None and right is None and top is None and bottom is None:
            self.__borderless = True
        else:
            self.__borderless = False

    @property
    def horizontal(self):
        """Return sum of left and right extents."""
        return self.left + self.right

    @property
    def vertical(self):
        """Return sum of top and bottom extents."""
        return self.top + self.bottom

    def __eq__(self, other):
        return ((self.left, self.right, self.top, self.bottom) ==
                (other.left, other.right, other.top, other.bottom))

    def __ne__(self, other):
        return not self == other

    def __nonzero__(self):
        return not self.__borderless
        #return self.top != 0 or self.bottom != 0 or \
        #       self.left != 0 or self.right != 0

    def __repr__(self):
        return '<Extents left=%s, right=%s, top=%s, bottom=%s>' % \
               (self.left, self.right, self.top, self.bottom)


class Strut(object):

    """Information about area reserved by windows (docks, panels, pagers).
    
    For each desktop's edge there's a tuple: height/width, start_x/y, end_x/y

    """

    def __init__(self, left, right, top, bottom,
                 left_start_y=0, left_end_y=0, 
                 right_start_y=0, right_end_y=0,
                 top_start_x=0, top_end_x=0, 
                 bottom_start_x=0, bottom_end_x=0):
        self.left = (left, left_start_y, left_end_y)
        self.right = (right, right_start_y, right_end_y)
        self.top = (top, top_start_x, top_end_x)
        self.bottom = (bottom, bottom_start_x, bottom_end_x)

    def __repr__(self):
        return '<Strut left=%s, right=%s, top=%s, bottom=%s>' % \
               (self.left, self.right, self.top, self.bottom)


class Layout(object):

    """Encapsulates layout of desktops (or viewports).
    
    Examples::

      cols = 3, rows=2, orientation=ORIENTATION_HORZ, corner=CORNER_TOPLEFT

      0 1 2
      3 4 5

      cols = 3, rows=2, orientation=ORIENTATION_VERT, corner=CORNER_TOPLEFT

      0 2 4
      1 3 5

      cols = 3, rows=2, orientation=ORIENTATION_HORZ, corner=CORNER_TOPRIGHT

      2 1 0
      5 3 4
    
    """

    # Orientations
    ORIENTATION_HORZ = 0 #XObject.atom('_NET_WM_ORIENTATION_HORZ')
    """Horizontal orientation."""
    ORIENTATION_VERT = 1 #XObject.atom('_NET_WM_ORIENTATION_VERT')
    """Vertical orientation."""

    # Starting corners
    CORNER_TOPLEFT = 0 #XObject.atom('_NET_WM_TOPLEFT')
    """Starting from top-left corner."""
    CORNER_TOPRIGHT = 1 #XObject.atom('_NET_WM_TOPRIGHT')
    """Starting from top-right corner."""
    CORNER_BOTTOMRIGHT = 2 #XObject.atom('_NET_WM_BOTTOMRIGHT')
    """Starting from bottom-right corner."""
    CORNER_BOTTOMLEFT = 3 #XObject.atom('_NET_WM_BOTTOMLEFT')
    """Starting from bottom-left corner."""

    def __init__(self, cols, rows, 
                 orientation=ORIENTATION_HORZ, corner=CORNER_TOPLEFT):
        self.cols = cols
        self.rows = rows
        self.orientation = orientation
        self.corner = corner

    def __eq__(self, other):
        return ((self.cols, self.rows, self.orientation, self.corner) ==
                (other.cols, other.rows, other.orientation, other.corner))

    def __repr__(self):
        return '<Layout cols=%s, rows=%s, orientation=%s, corner=%s>' % \
               (self.cols, self.rows, self.orientation, self.corner)

