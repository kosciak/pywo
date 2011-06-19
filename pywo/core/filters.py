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

"""Window filters.

All filters are callable, and accept :class:`~pywo.core.windows.Window` 
instance as an argument.

"""

import logging

from pywo.core import Window, WindowManager, Type, State


__author__ = "Wojciech 'KosciaK' Pietrzok"


log = logging.getLogger(__name__)


class IncludeType(object):

    """Return only windows with any of specified types."""

    def __init__(self, *types):
        self.allowed_types = types

    def __call__(self, window):
        type = window.type
        # NOTE: Some normal windows have no type set (e.g. tvtime)
        for allowed_type in self.allowed_types:
            if allowed_type in type:
                return True
        return False


class ExcludeType(object):

    """Return only windows without specified types."""

    def __init__(self, *types):
        self.not_allowed_types = types

    def __call__(self, window):
        type = window.type
        for not_allowed_type in self.not_allowed_types:
            if not_allowed_type in type:
                return False
        return True


class IncludeState(object):

    """Return only windows with any of specified states."""

    def __init__(self, *states):
        self.allowed_states = states

    def __call__(self, window):
        state = window.state
        for allowed_state in self.allowed_states:
            if allowed_state in state:
                return True
        return False


class ExcludeState(object):

    """Return only windows without specified types."""

    def __init__(self, *states):
        self.not_allowed_states = states

    def __call__(self, window):
        state = window.state
        for not_allowed_state in self.not_allowed_states:
            if not_allowed_state in state:
                return False
        return True


class Desktop(object):

    """Return only windows on specified (or current) desktop."""

    def __init__(self, desktop=None):
        self.desktop = desktop or WindowManager().desktop 

    def __call__(self, window):
        win_desktop = window.desktop
        return win_desktop == self.desktop or \
               win_desktop == Window.ALL_DESKTOPS


class Workarea(Desktop):

    """Return only windows on current workarea.
    
    NOTE: Overlap filter (combined with Desktop) should be used instead!
    
    """

    def __init__(self):
        Desktop.__init__(self)
        self.workarea = WindowManager().workarea_geometry

    def __call__(self, window):
        if not Desktop.__call__(self, window):
            return False
        geometry = window.geometry
        return geometry.x < self.workarea.x2 and \
               geometry.x2 > self.workarea.x and \
               geometry.y < self.workarea.y2 and \
               geometry.y2 > self.workarea.y


class Overlap(object):

    """Return windows that are inside (or are adjacent to) given geometry.
    
    NOTE: Combine with Desktop filter to get only windows on current desktop!
    
    """

    def __init__(self, geometry, adjacent=False):
        self.geometry = geometry
        self.adjacent = adjacent

    def __call__(self, window):
        intersection = window.geometry & self.geometry
        if not intersection:
            return False
        if not self.adjacent and \
           not intersection.area:
            return False
        return True


class ExcludeId(object):

    """Return windows with id not in the exlcude list."""

    def __init__(self, *exclude_ids):
        self.exclude_ids = exclude_ids

    def __call__(self, window):
        return window.id not in self.exclude_ids


class AND(object):

    """Combine filters."""

    def __init__(self, *filters):
        self.filters = filters

    def __call__(self, window):
        for filter in self.filters:
            if not filter(window):
                return False
        return True


ALL_FILTER = lambda window: True
"""Accept all windows."""

NORMAL_TYPE = IncludeType(Type.NORMAL, Type.NONE)
"""Accept windows with `NORMAL` or no :class:`~pywo.core.windows.Type` set."""
STANDARD_TYPE = ExcludeType(Type.DESKTOP, Type.DOCK, 
                            Type.SPLASH, Type.MENU, Type.TOOLBAR)
"""Accept windows **not** with :class:`~pywo.core.windows.Type`: 
`DESKTOP`, `DOCK`, `SPLASH`, `MENU`, `TOOLBAR`."""
NORMAL_STATE = ExcludeState(State.MODAL, State.SHADED, State.HIDDEN,
                            State.MAXIMIZED, State.FULLSCREEN)
"""Accept windows **not** with :class:`~pywo.core.windows.State`: 
`MODAL`, `SHADED`, `HIDDEN`, `MAXIMIZED`, `FULLSCREEN`."""
NORMAL = AND(NORMAL_TYPE, NORMAL_STATE)
"""Accept windows with `NORMAL_TYPE` and `NORMAL_STATE`."""
STANDARD = AND(STANDARD_TYPE, NORMAL_STATE)
"""Accept windows with `STANDARD_TYPE` and `NORMAL_STATE`."""

