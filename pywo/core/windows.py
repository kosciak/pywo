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

from pywo.core.basic import CustomTuple
from pywo.core.basic import Gravity, Geometry, Extents, Strut
from pywo.core.enums import WindowType, State, Mode, ManagerType, Hacks
from pywo.core.xlib import XObject


__author__ = "Wojciech 'KosciaK' Pietrzok, Antti Kaihola"


log = logging.getLogger(__name__)


class Window(XObject):

    """Window object."""

    # _NET_WM_DESKTOP returns this value when in STATE_STICKY
    ALL_DESKTOPS = 0xFFFFFFFF
    """Visible on all :ref:`desktops <desktop>`."""

    def __init__(self, win_id):
        XObject.__init__(self, win_id)

    @property
    def type(self):
        """Return tuple of window's :class:`WindowType`(s)."""
        # _NET_WM_WINDOW_TYPE, ATOM[]/32
        type = self.get_property('_NET_WM_WINDOW_TYPE')
        if not type:
            return CustomTuple([WindowType.NONE])
        return CustomTuple(type.value)

    @property
    def state(self):
        """Return tuple of window's state(s)."""
        # _NET_WM_STATE, ATOM[]
        state = self.get_property('_NET_WM_STATE')
        if not state:
            return CustomTuple()
        return CustomTuple(state.value)

    @property
    def parent_id(self):
        """Return window's parent id."""
        parent = self._win.get_wm_transient_for()
        if parent:
            return parent.id
        else:
            return None

    @property
    def parent(self):
        """Return window's parent."""
        parent_id = self.parent_id
        if parent_id:
            return Window(parent_id)
        else:
            return None

    @property
    def name(self):
        """Return window's name."""
        # _NET_WM_NAME, UTF8_STRING
        name = self.get_property('_NET_WM_NAME')
        if not name:
            name = self._win.get_full_property(Xatom.WM_NAME, 0)
            if not name:        
                return ''
        return name.value

    @property
    def class_name(self):
        """Return window's class name."""
        class_name = self._win.get_wm_class()
        if class_name:
            return '.'.join(class_name)
        return ''

    @property
    def client_machine(self):
        """Return name of window's client machine."""
        client = self._win.get_wm_client_machine()
        return client

    @property
    def desktop(self):
        """Return :ref:`desktop` number the window is on.

        Returns :const:`ALL_DESKTOPS` if window is sticky.

        """
        # _NET_WM_DESKTOP desktop, CARDINAL/32
        desktop = self.get_property('_NET_WM_DESKTOP')
        if not desktop:
            return 0
        return desktop.value[0]

    def set_desktop(self, desktop_id):
        """Move window to given :ref:`desktop`."""
        desktop_id = int(desktop_id)
        if desktop_id < 0:
            desktop_id = 0
        event_type = self.atom('_NET_WM_DESKTOP')
        data = [desktop_id, 
                0, 0, 0, 0]
        mask = X.PropertyChangeMask
        self.send_event(data, event_type, mask)

    # TODO: viewport_position, viewport, set_viewport

    def __strut(self):
        """Return raw strut info."""
        # _NET_WM_STRUT, left, right, top, bottom, CARDINAL[4]/32
        strut = self.get_property('_NET_WM_STRUT')
        if strut:
            return strut.value
        else:
            return ()

    def __strut_partial(self):
        """Return raw strut partial info."""
        # _NET_WM_STRUT_PARTIAL, left, right, top, bottom, 
        #                        left_start_y, left_end_y,
        #                        right_start_y, right_end_y, 
        #                        top_start_x, top_end_x, 
        #                        bottom_start_x, bottom_end_x, 
        #                        CARDINAL[12]/32
        strut_partial = self.get_property('_NET_WM_STRUT_PARTIAL')
        if strut_partial:
            return strut_partial.value
        else:
            return ()

    @property
    def strut(self):
        """Return :class:`~pywo.core.basic.Strut`."""
        strut_partial = self.__strut_partial()
        if strut_partial:
            # Try strut_partial first, with full info about reserved area
            return Strut(*strut_partial)
        strut = self.__strut()
        if strut:
            # Fallback to strut - only info about width/height
            return Strut(strut[0], strut[1], strut[2], strut[3], 
                         0, 0, 0, 0, 0, 0, 0, 0)
        return None

    def __extents(self):
        """Return raw extents info."""
        # _NET_FRAME_EXTENTS, left, right, top, bottom, CARDINAL[4]/32
        extents = self.get_property('_NET_FRAME_EXTENTS')
        ## NOTE:          self.get_property('_GTK_FRAME_EXTENTS')
        if extents:
            return extents.value
        else: 
            return ()

    @property
    def extents(self):
        """Return window's :class:`~pywo.core.basic.Extents`."""
        extents = self.__extents()
        if not extents and self.wm_type in Hacks.CALCULATE_EXTENTS:
            # Hack for Blackbox, IceWM, Sawfish, Window Maker
            win = self._win
            parent = win.query_tree().parent
            if parent.id == self._root_id:
                return Extents(None, None, None, None)
            if win.get_geometry().width == parent.get_geometry().width and \
               win.get_geometry().height == parent.get_geometry().height:
                win, parent = parent, parent.query_tree().parent
            if parent.id == self._root_id:
                return Extents(None, None, None, None)
            win_geo = win.get_geometry()
            parent_geo = parent.get_geometry()
            border_widths = win_geo.border_width + parent_geo.border_width
            parent_border = parent_geo.border_width*2
            left = win_geo.x + border_widths
            top = win_geo.y + border_widths
            right = parent_geo.width - win_geo.width - left + parent_border
            bottom = parent_geo.height - win_geo.height - top + parent_border
            extents = (left, right, top, bottom)
        elif not extents:
            extents = (None, None, None, None)
        elif ManagerType.OPENBOX in self.wm_type and \
             State.OB_UNDECORATED in self.state:
            # TODO: recognize 'retain border when undecorated' setting
            extents = (1, 1, 1, 1) # works for retain border
            #extents = (0, 0, 0, 0) # if border is not retained
        return Extents(*extents)

    def __geometry(self):
        """Return raw geometry info (translated if needed)."""
        geometry = self._win.get_geometry()
        parent_geo = self._win.query_tree().parent.get_geometry()
        if self.wm_type in Hacks.PARENT_XY:
            # Hack for Fluxbox, Window Maker
            geometry.x = parent_geo.x
            geometry.y = parent_geo.y
        return (geometry.x, geometry.y, 
                geometry.width, geometry.height)

    @property
    def geometry(self):
        """Return window's :class:`~pywo.core.basic.Geometry`.

        (x, y) coordinates are the top-left corner of the window.
        Window position is relative to the left-top corner of 
        current :ref:`viewport`.
        Position and size *includes* window's extents!
        Position is translated if needed.

        """
        x, y, width, height = self.__geometry()
        extents = self.extents
        if self.wm_type not in Hacks.DONT_TRANSLATE_COORDS and \
           not (ManagerType.METACITY in self.wm_type and not extents):
            # NOTE: in Metacity for windows with no extents 
            #       returned translated coords were invalid (0, 0)
            # if neeeded translate coords and multiply them by -1
            translated = self._translate_coords(x, y)
            x = -translated.x
            y = -translated.y
        if self.wm_type in Hacks.ADJUST_TRANSLATE_COORDS:
            translated = self._translate_coords(x, y)
            x -= translated.x
            y -= translated.y
        if self.wm_type in Hacks.ADJUST_GEOMETRY:
            # Used in Compiz, KWin, E16, IceWM, Blackbox
            x -= extents.left
            y -= extents.top
        # FIXME: invalid geometry if border_width > 0 in raw_geometry
        return Geometry(x, y,
                        width + extents.horizontal,
                        height + extents.vertical)

    def set_geometry(self, geometry, on_resize=Gravity(0, 0)):
        """Move or resize window. 

        Use provided :class:`~pywo.core.basic.Geometry`, in case of resize
        adjust position using :class:`~pywo.core.basic.Gravity`.
        Postion (relative to current :ref:`viewport`) and size must include 
        window's extents. 

        """
        # FIXME: probably doesn't work correctly with windows with border_width
        extents = self.extents
        x = geometry.x
        y = geometry.y
        width = geometry.width - extents.horizontal
        height = geometry.height - extents.vertical
        geometry_size = (width, height)
        current = self.__geometry()
        hints = self._win.get_wm_normal_hints()
        # This is a fix for WINE, OpenOffice and KeePassX windows
        if hints and hints.win_gravity == X.StaticGravity:
            x += extents.left
            y += extents.top
        # Reduce size to maximal allowed value
        if hints and hints.max_width: 
            width = min([width, hints.max_width])
        if hints and hints.max_height:
            height = min([height, hints.max_height])
        # Don't try to set size lower then minimal
        if hints and hints.min_width: 
            width = max([width, hints.min_width])
        if hints and hints.min_height:
            height = max([height, hints.min_height])
        # Set correct size if it is incremental, take base in account
        if hints and hints.width_inc: 
            if hints.base_width:
                base = hints.base_width
            else:
                base = current[2] % hints.width_inc
            width = ((width - base) / hints.width_inc) * hints.width_inc
            width += base
            if hints.min_width and width < hints.min_width:
                width += hints.width_inc
        if hints and hints.height_inc:
            if hints.base_height:
                base = hints.base_height
            else:
                base = current[3] % hints.height_inc
            height = ((height - base) / hints.height_inc) * hints.height_inc
            height += base
            if hints.height_inc and height < hints.min_height:
                height += hints.height_inc
        # Adjust position after size change
        if (width, height) != geometry_size:
            x = x + (geometry_size[0] - width) * on_resize.x
            y = y + (geometry_size[1] - height) * on_resize.y
        self._win.configure(x=x, y=y, width=width, height=height)

    def moveresize(self, geometry):
        """Works like :meth:`set_geometry`, but using ``_NET_MOVERESIZE_WINDOW``

        This gives finer control: 

        * it allows to use gravity, so there are no problems with static windows
        * x, y coordinates includes window's extents
        * allow to move part of the window outside the workarea, while 
          configure will resize window to fit workarea

        .. warning::
          It seems that x,y coords must be unsigned ints!!! 
          So it is not possible to move window to the left :ref:`viewport`!
          Not sure it it is EWMH, Xlib, or python-xlib fault...
          But it makes _NET_MOVERESIZE_WINDOW rather useless...

        """
        # TODO: check the border_width issue
        # TODO: what about max/min/incremental size?
        event_type = self.atom('_NET_MOVERESIZE_WINDOW')
        mask = X.SubstructureRedirectMask
        flags = 1 << 8 | 1 << 9 | 1 << 10 | 1 << 11 | 1 << 13
        data = [X.NorthWestGravity | flags,
                max([0, geometry.x]),
                max([0, geometry.y]),
                geometry.width,
                geometry.height]
        self.send_event(data, event_type, mask)

    def activate(self):
        """Make this window active (and unshade, unminimize)."""
        # NOTE: In Metacity this WON'T change desktop to window's desktop!
        event_type = self.atom('_NET_ACTIVE_WINDOW')
        mask = X.SubstructureRedirectMask
        data = [0, 0, 0, 0, 0]
        self.send_event(data, event_type, mask)
        # NOTE: Previously used for activating (didn't unshade/unminimize)
        #       Need to test if setting X.Above is needed in various WMs
        #self._win.set_input_focus(X.RevertToNone, X.CurrentTime)
        #self._win.configure(stack_mode=X.Above)

    def iconify(self, mode):
        """Iconify (minimize) window."""
        state = self._win.get_wm_state().state
        if mode == 1 or \
           mode == 2 and state == Xutil.NormalState:
            set_state = Xutil.IconicState
        if mode == 0 or \
           mode == 2 and state == Xutil.IconicState:
            set_state = Xutil.NormalState
        event_type = self.atom('WM_CHANGE_STATE')
        mask = X.SubstructureRedirectMask
        data = [set_state,
                0, 0, 0, 0]
        self.send_event(data, event_type, mask)

    def maximize(self, mode,
                 vert=State.MAXIMIZED_VERT, 
                 horz=State.MAXIMIZED_HORZ):
        """Maximize window.

        If you want to maximize only horizontally use ``vert=False``
        If you want to maximize only vertically use ``horz=False``

        """
        data = [mode, 
                horz,
                vert,
                0, 0]
        self.__change_state(data)

    def shade(self, mode):
        """Shade window (if supported by window manager)."""
        data = [mode, 
                State.SHADED,
                0, 0, 0]
        self.__change_state(data)

    def fullscreen(self, mode):
        """Make window fullscreen (if supported by window manager)."""
        data = [mode, 
                State.FULLSCREEN,
                0, 0, 0]
        self.__change_state(data)

    def sticky(self, mode):
        """Make window sticky (if supported by window manager)."""
        data = [mode, 
                State.STICKY,
                0, 0, 0]
        self.__change_state(data)

    def always_above(self, mode):
        """Make window always above others (if supported by window manager)."""
        data = [mode, 
                State.ABOVE,
                0, 0, 0]
        self.__change_state(data)

    def always_below(self, mode):
        """Make window always below others (if supported by window manager)."""
        data = [mode, 
                State.BELOW,
                0, 0, 0]
        self.__change_state(data)

    def reset(self, full=False):
        """Reset window's state.

        Uniconify, unset fullscreen, unmaximize, unshade. 
        If ``full == True`` unset sticky, always above / below.

        """
        self.iconify(Mode.UNSET)
        self.fullscreen(Mode.UNSET)
        self.maximize(Mode.UNSET)
        self.shade(Mode.UNSET)
        if full:
            self.sticky(Mode.UNSET)
            self.always_above(Mode.UNSET)
            self.always_below(Mode.UNSET)

    def close(self):
        """Close window."""
        event_type = self.atom('_NET_CLOSE_WINDOW')
        mask = X.SubstructureRedirectMask
        data = [0, 0, 0, 0, 0]
        self.send_event(data, event_type, mask)

    def destroy(self):
        """Unmap and destroy window."""
        self._win.unmap()
        self._win.destroy()

    def __change_state(self, data):
        """Send ``_NET_WM_STATE`` event to the root window."""
        event_type = self.atom('_NET_WM_STATE')
        mask = X.SubstructureRedirectMask
        self.send_event(data, event_type, mask)

    def visual_bell(self, color_name="red", line_width=4, duration=0.125):
        """Show border around window."""
        osd = self.osd_rectangle(self.geometry, color_name, line_width)
        osd.blink(duration)

    def __eq__(self, other):
        return self.id == other.id

    def __ne__(self, other):
        return not self.id == other.id

    def __repr__(self):
        return '<Window id=%s>' % (self.id,)

    def debug_info(self, logger=log):
        """Print full window's info, for debug use only."""
        logger.info('-= Current Window =-')
        win = self._win
        logger.info('ID=%s' % self.id)
        logger.info(self.list_properties())
        logger.info('Client_machine="%s"' % self.client_machine)
        logger.info('Name="%s"' % self.name)
        logger.info('Class="%s"' % self.class_name)
        logger.info('WindowType=%s' % [self.atom_name(e) for e in self.type])
        logger.info('State=%s' % [self.atom_name(e) for e in self.state])
        logger.info('WM State=%s' % win.get_wm_state())
        logger.info('Desktop=%s' % self.desktop)
        logger.info('Extents=%s' % self.extents)
        logger.info('Extents_raw=%s' % [str(e) for e in self.__extents()])
        logger.info('Geometry=%s' % self.geometry)
        logger.info('Geometry_raw=%s' % getattr(win.get_geometry(), '_data'))
        geometry = self._win.get_geometry()
        translated = self._translate_coords(geometry.x, geometry.y)
        logger.info('Geometry_translated=%s' % getattr(translated, '_data'))
        logger.info('Strut=%s' % self.strut)
        logger.info('Parent=%s %s' % (self.parent_id, self.parent))
        logger.info('Normal_hints=%s' % getattr(win.get_wm_normal_hints(), 
                                                '_data'))
        log.info('Hints=%s' % self._win.get_wm_hints())
        logger.info('Attributes=%s' % getattr(win.get_attributes(), '_data'))
        logger.info('Query_tree=%s' % getattr(win.query_tree(), '_data'))

