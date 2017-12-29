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

"""Classes and functions related to windows and window managers.

.. seealso::

    * :doc:`/definitions` for reference of used terms.
    * :doc:`xlib` for methods common to both :class:`Window` 
      and :class:`WindowManager`

"""


from pywo.core.basic import CustomTuple
from pywo.core.xlib import XObject


class WindowType(object):

    """Enum of windows types."""

    DESKTOP = XObject.atom('_NET_WM_WINDOW_TYPE_DESKTOP')
    """Desktop."""
    DOCK = XObject.atom('_NET_WM_WINDOW_TYPE_DOCK')
    """Dock window (for example panels)."""
    TOOLBAR = XObject.atom('_NET_WM_WINDOW_TYPE_TOOLBAR')
    """Toolbar window."""
    MENU = XObject.atom('_NET_WM_WINDOW_TYPE_MENU')
    """Menu window."""
    UTILITY = XObject.atom('_NET_WM_WINDOW_TYPE_UTILITY')
    """Utility window."""
    SPLASH = XObject.atom('_NET_WM_WINDOW_TYPE_SPLASH')
    """Splash dialog."""
    DIALOG = XObject.atom('_NET_WM_WINDOW_TYPE_DIALOG')
    """Modal dialog."""
    NORMAL = XObject.atom('_NET_WM_WINDOW_TYPE_NORMAL')
    """Normal window."""
    NONE = -1
    """No `WindowType` specified."""


class State(object):

    """Enum of window states."""

    # States described by EWMH
    MODAL = XObject.atom('_NET_WM_STATE_MODAL')
    """Modal dialog."""
    STICKY = XObject.atom('_NET_WM_STATE_STICKY')
    """Sticky - show on all :ref:`desktops <desktop>` 
    / :ref:`viewports <viewport>`."""
    MAXIMIZED_VERT = XObject.atom('_NET_WM_STATE_MAXIMIZED_VERT')
    """Maximized vertically."""
    MAXIMIZED_HORZ = XObject.atom('_NET_WM_STATE_MAXIMIZED_HORZ')
    """Maximized horizontally."""
    MAXIMIZED = (MAXIMIZED_VERT, MAXIMIZED_HORZ)
    """Maximized both vertically and horizontally."""
    SHADED = XObject.atom('_NET_WM_STATE_SHADED')
    """Shaded (only title bar is visible)."""
    SKIP_TASKBAR = XObject.atom('_NET_WM_STATE_SKIP_TASKBAR')
    """Don't show window in the taskbar."""
    SKIP_PAGER = XObject.atom('_NET_WM_STATE_SKIP_PAGER')
    """Don't show window in the pager."""
    HIDDEN = XObject.atom('_NET_WM_STATE_HIDDEN')
    """Hidden window (for example when iconified)."""
    FULLSCREEN = XObject.atom('_NET_WM_STATE_FULLSCREEN')
    """Fullscreen."""
    ABOVE = XObject.atom('_NET_WM_STATE_ABOVE')
    """Above all other windows."""
    BELOW = XObject.atom('_NET_WM_STATE_BELOW')
    """Below all other windows."""
    DEMANDS_ATTENTION = XObject.atom('_NET_WM_STATE_DEMANDS_ATTENTION')
    """Demands attention."""
    # Window managers specific states
    OB_UNDECORATED = XObject.atom('_OB_WM_STATE_UNDECORATED')
    """Borderless (only in Openbox)."""


class Mode(object):

    """Enum of mode values. 
    
    Used while changing window's states.
    
    """

    UNSET = 0
    """Unset state."""
    SET = 1
    """Set state."""
    TOGGLE = 2
    """Toggle state."""


class ManagerType(object):

    """Enum of window managers types."""

    COMPIZ = 1
    METACITY = 2
    KWIN = 3
    XFWM = 4
    OPENBOX = 5
    FLUXBOX = 6
    BLACKBOX = 7
    ICEWM = 8
    ENLIGHTMENT = 9
    WINDOW_MAKER = 10
    SAWFISH = 11
    PEKWM = 12
    GNOME_SHELL = 13
    UNKNOWN = -1


class Hacks(object):

    """List of hacks caused by EWMH, ICCCM implementation inconsistencies."""

    DONT_TRANSLATE_COORDS = CustomTuple([
        ManagerType.COMPIZ, 
        ManagerType.FLUXBOX, 
        ManagerType.WINDOW_MAKER,
        #ManagerType.GNOME_SHELL,
    ])
    """Don't translate coordinates of the window."""

    ADJUST_GEOMETRY = CustomTuple([
        ManagerType.COMPIZ, 
        ManagerType.KWIN, 
        ManagerType.ENLIGHTMENT, 
        ManagerType.ICEWM, 
        ManagerType.BLACKBOX,
        ManagerType.GNOME_SHELL,
    ])
    """Adjust `Geometry`."""

    ADJUST_TRANSLATE_COORDS = CustomTuple([
        ManagerType.GNOME_SHELL,
    ])
    """Adjust 'Geometry` by translated coordinates of the window."""

    PARENT_XY = CustomTuple([
        ManagerType.FLUXBOX, 
        ManagerType.WINDOW_MAKER,
        #ManagerType.GNOME_SHELL,
    ])
    """Use coordinates from window's parent."""

    CALCULATE_EXTENTS = CustomTuple([
        ManagerType.BLACKBOX, 
        ManagerType.ICEWM,
        ManagerType.SAWFISH,
        ManagerType.WINDOW_MAKER,
        ManagerType.UNKNOWN,
    ])
    """Calculate `Extents` values if not provided by window manager."""

