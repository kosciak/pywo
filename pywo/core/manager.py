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


import logging

from Xlib import X, Xutil, Xatom

from pywo.core.basic import Position, Size, Geometry
from pywo.core.basic import Layout
from pywo.core.enums import ManagerType
from pywo.core.xlib import XObject
from pywo.core.windows import Window


__author__ = "Wojciech 'KosciaK' Pietrzok, Antti Kaihola"


log = logging.getLogger(__name__)


class WindowManager(XObject):
    
    """Window Manager (or root window in X programming terms).
    
    WindowManager's :attr:`_win` refers to the root window.

    `WindowManager` is a Singleton.

    """

    # Instance of the WindowManager class, make it Singleton.
    __INSTANCE = None

    def __new__(cls):
        if cls.__INSTANCE:
            return cls.__INSTANCE
        manager = object.__new__(cls)
        XObject.__init__(manager)
        cls.__INSTANCE = manager
        manager.update_type()
        return manager

#    def __init__(self):
#        XObject.__init__(self)
#        self.update_type()

    @property
    def name(self):
        """Return window manager's name.

        ``''`` is returned if window manager doesn't support EWMH.

        """
        # _NET_SUPPORTING_WM_CHECK, WINDOW/32
        win_id = self.get_property('_NET_SUPPORTING_WM_CHECK')
        if not win_id:
            return ''
        win = XObject(win_id.value[0])
        name = win.get_property('_NET_WM_NAME')
        if name:
            return name.value
        else:
            return ''

    @property
    def type(self):
        """Return tuple of window manager's type(s)."""
        return self.wm_type
    
    def update_type(self):
        """Update window manager's type."""
        recognize = {'compiz': ManagerType.COMPIZ, 
                     'metacity': ManagerType.METACITY,
                     'kwin': ManagerType.KWIN, 
                     'xfwm': ManagerType.XFWM, 
                     'openbox': ManagerType.OPENBOX, 
                     'fluxbox': ManagerType.FLUXBOX,
                     'blackbox': ManagerType.BLACKBOX, 
                     'icewm': ManagerType.ICEWM,
                     'e1': ManagerType.ENLIGHTMENT, 
                     'sawfish': ManagerType.SAWFISH,
                     'window maker': ManagerType.WINDOW_MAKER, 
                     'pekwm': ManagerType.PEKWM,
                     'gnome shell': ManagerType.GNOME_SHELL,
                    }
        name = self.name.lower()
        XObject.set_wm_type(ManagerType.UNKNOWN)
        for name_part, wm_type in recognize.items():
            if name_part in name:
                XObject.set_wm_type(wm_type)

    @property
    def desktops(self):
        """Return number of :ref:`desktops <desktop>`.
        
        Number of desktops may differ from ``desktop_layout.cols*rows``
        
        """
        # _NET_NUMBER_OF_DESKTOPS, CARDINAL/32
        number = self.get_property('_NET_NUMBER_OF_DESKTOPS')
        if not number:
            return 1
        return number.value[0]

    @property
    def desktop_names(self):
        """Return list of :ref:`desktop` names.

        Not all Window Managers support desktop names, in this case 
        empty list is returned.
        Length of list of names may differ from number of desktops!

        """
        # _NET_DESKTOP_NAMES, UTF8_STRING[]
        names = self.get_property('_NET_DESKTOP_NAMES')
        if not names:
            return []
        return names.value.decode('utf-8').split('\x00')[:-1]

    # TODO: set_desktop_name ???
    # TODO: add_desktop, remove_desktop

    @property
    def desktop(self):
        """Return current :ref:`desktop` number."""
        # _NET_CURRENT_DESKTOP desktop, CARDINAL/32
        desktop = self.get_property('_NET_CURRENT_DESKTOP')
        return desktop.value[0]

    def set_desktop(self, num):
        """Change current :ref:`desktop`."""
        num = int(num)
        if num < 0:
            num = 0
        event_type = self.atom('_NET_CURRENT_DESKTOP')
        data = [num, 
                0, 0, 0, 0]
        mask = X.PropertyChangeMask
        self.send_event(data, event_type, mask)

    @property
    def desktop_size(self):
        """Return Size of current :ref:`desktop`."""
        # _NET_DESKTOP_GEOMETRY width, height, CARDINAL[2]/32
        geometry = self.get_property('_NET_DESKTOP_GEOMETRY').value
        return Size(geometry[0], geometry[1])

    # TODO: set_desktop_size?!?, or set_viewports(columns, rows)

    @property
    def desktop_layout(self):
        """Return :ref:`desktops <desktop>` :class:`~pywo.core.basic.Layout`, 
        as set by pager."""
        # _NET_DESKTOP_LAYOUT, orientation, columns, rows, starting_corner 
        #                      CARDINAL[4]/32
        layout = self.get_property('_NET_DESKTOP_LAYOUT')
        if not layout:
            return None
        orientation, cols, rows, corner = layout.value
        desktops = self.desktops
        # NOTE: needs more testing...
        cols = cols or (desktops / rows + min([1, desktops % rows]))
        rows = rows or (desktops / cols + min([1, desktops % cols]))
        return Layout(cols, rows, orientation, corner)

    @property
    def viewport_position(self):
        """Return position of current :ref:`viewport`.

        Position is relative to :ref:`desktop`.

        """
        # _NET_DESKTOP_VIEWPORT x, y, CARDINAL[][2]/32
        viewport = self.get_property('_NET_DESKTOP_VIEWPORT').value
        # TODO: Might not work correctly on all WMs
        return Position(viewport[0], viewport[1])

    def set_viewport_position(self, x, y):
        """Change current :ref:`viewport` position."""
        event_type = self.atom('_NET_DESKTOP_VIEWPORT')
        data = [x, 
                y, 
                0, 0, 0]
        mask = X.PropertyChangeMask
        self.send_event(data, event_type, mask)

    def set_viewport(self, viewport):
        """Change current :ref:`viewport` (similar to :meth:`set_desktop`)."""
        if viewport < 0:
            viewport = 0
        desktop_size = self.desktop_size
        layout = self.viewport_layout
        x = desktop_size.width / layout.cols * (viewport % layout.cols)
        y = desktop_size.height / layout.rows * (viewport / layout.cols)
        self.set_viewport_position(x, y)

    @property
    def viewport_layout(self):
        """Return :ref:`viewports <viewport>` :class:`~pywo.core.basic.Layout`, 
        as set by pager.

        Some Window Managers use scrolling instead of pagination, 
        so it is possible to set viewport to any position inside :ref:`desktop`.

        """
        desktop_size = self.desktop_size
        workarea_size = self.workarea_geometry
        cols = desktop_size.width / workarea_size.width
        rows = desktop_size.height / workarea_size.height
        return Layout(cols, rows)

    @property
    def workarea_geometry(self):
        """Return geometry of current :ref:`workarea`.
        
        Position is relative to current :ref:`viewport`.
        
        """
        # _NET_WORKAREA, x, y, width, height CARDINAL[][4]/32
        workarea = self.get_property('_NET_WORKAREA').value
        # NOTE: this will return geometry for first, not current!
        #       what about all workareas, not only the current one?
        # TODO: multi monitor support by returning workarea for current monitor?
        return Geometry(workarea[0], workarea[1], 
                        workarea[2], workarea[3])

    # TODO: Maybe add Window.current_screen()?
    def nearest_screen_geometry(self, geometry):
        """Return :class:`~pywo.core.basic.Geometry` of the :ref:`screen` 
        best matching the given rectangle.
        
        Position is relative to current :ref:`viewport`.
        
        """
        screens_by_intersection = ((screen & geometry, screen)
                                   for screen in self.screen_geometries())
        screens_by_area = ((intersection.area, screen)
                           for intersection, screen in screens_by_intersection
                           if intersection)
        largest_area, screen = sorted(screens_by_area)[-1]
        return screen & self.workarea_geometry

    def active_window_id(self):
        """Return id of active window."""
        # _NET_ACTIVE_WINDOW, WINDOW/32
        win_id = self.get_property('_NET_ACTIVE_WINDOW')
        if win_id:
            return win_id.value[0]
        return None

    def active_window(self):
        """Return active window."""
        window_id = self.active_window_id()
        if window_id:
            return Window(window_id)
        return None

    @staticmethod
    def get_window(window_id):
        """Return Window with given id."""
        window = Window(window_id)
        return window

    def windows_ids(self, stacking=True):
        """Return list of all windows' ids (newest/on top first)."""
        if stacking:
            windows_ids = self.get_property('_NET_CLIENT_LIST_STACKING').value
        else:
            windows_ids = self.get_property('_NET_CLIENT_LIST').value
        windows_ids.reverse()
        return windows_ids

    def windows(self, filter=None, match='', stacking=True):
        """Return list of all windows (newest/on top first)."""
        # TODO: regexp matching?
        windows_ids = self.windows_ids(stacking)
        windows = [Window(win_id) for win_id in windows_ids]
        if filter:
            windows = [window for window in windows if filter(window)]
        if match:
            windows = self.__name_matcher(windows, match)
        return windows

    def visual_bell(self, color_name="red", line_width=4, duration=0.125):
        """Show border around :ref:`workarea` on current :ref:`screen`."""
        active = self.active_window()
        nearest_geometry = self.nearest_screen_geometry(active.geometry)
        osd = self.osd_rectangle(nearest_geometry, color_name, line_width)
        osd.blink(duration)

    def __name_matcher(self, windows, match):
        """Filter and sort windows with matching name or class name."""
        match = match.strip().lower()
        # TODO: match.decode('utf-8') if not unicode
        desktop = self.desktop
        workarea = self.workarea_geometry
        def mapper(window, points=0):
            name = window.name.lower().decode('utf-8')
            if name == match:
                points += 200
            elif match in name:
                left = name.find(match)
                right = (name.rfind(match) - len(name) + len(match)) * -1
                points += 150 - min(left, right)
            if match in window.class_name.lower():
                points += 100
            try:
                geometry = window.geometry
            except:
                return (window, 0)
            if points and \
               (window.desktop == desktop or \
                window.desktop == Window.ALL_DESKTOPS):
                points += 50
                if geometry.x < workarea.x2 and \
                   geometry.x2 > workarea.x and \
                   geometry.y < workarea.y2 and \
                   geometry.y2 > workarea.y:
                    points += 100
            return (window, points)
        windows = map(mapper, windows)
        windows.sort(key=lambda win: win[1], reverse=True)
        windows = [win for win, points in windows if points]
        return windows

    def unregister_all(self):
        """Unregister all event handlers for all windows."""
        self._unregister_all()

    def __repr__(self):
        return '<WindowManager id=%s>' % (self.id,)

    def debug_info(self, logger=log):
        """Print full windows manager's info, for debug use only."""
        logger.info('-= Window Manager =-')
        logger.info('Name=%s' % self.name)
        logger.info('ManagerType=%s' % self.wm_type)
        logger.info(self.list_properties())
        #logger.info('Supported=%s' %  \
        #            [self.atom_name(atom) 
        #             for atom in self.get_property('_NET_SUPPORTED').value])
        logger.info('-= Desktops =-')
        logger.info('Layout=%s' % self.desktop_layout)
        logger.info('Names=%s' % self.desktop_names)
        logger.info('Total=%s' % self.desktops)
        logger.info('Current=%s' % self.desktop)
        logger.info('Size=%s' % self.desktop_size)
        logger.info('-= Viewports =-')
        logger.info('Layout=%s' % self.viewport_layout)
        logger.info('Position=%s' % self.viewport_position)
        logger.info('-= Workarea =-')
        logger.info('Geometry=%s' % self.workarea_geometry)
        logger.info('-= Strut =-')
        struts = [win.strut for win in self.windows()]
        logger.info('[%s]' %  \
                    ', '.join([str(strut) for strut in struts if strut]))
        logger.info('-= Screens =-')
        screens = self.screen_geometries()
        logger.info('Total=%s' % len(screens))
        logger.info('Geometries=[%s]' % \
                    ', '.join([str(geo) for geo in screens]))

