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

"""Connection with X Server, and handling all communication."""

import logging
import time

# NOTE: without import Xlib.threaded python-xlib is not thread-safe!
from Xlib import threaded
from Xlib import X, XK, error
from Xlib.display import Display
from Xlib.protocol.event import ClientMessage
from Xlib.ext import shape

from pywo.core.basic import CustomTuple, Geometry
from pywo.core.dispatch import EventDispatcher


__author__ = "Wojciech 'KosciaK' Pietrzok, Antti Kaihola"


log = logging.getLogger(__name__)


class XObject(object):

    """Abstract base class for classes communicating with X Server.

    Encapsulates common methods for communication with X Server.

    """

    # TODO: setting Display, not only default one
    __DISPLAY = Display()
    __EVENT_DISPATCHER = EventDispatcher(__DISPLAY)
    __BAD_ACCESS = error.CatchError(error.BadAccess)

    # List of recognized key modifiers
    __KEY_MODIFIERS = {'Alt': X.Mod1Mask,
                       'Ctrl': X.ControlMask,
                       'Shift': X.ShiftMask,
                       'Super': X.Mod4Mask,
                       'NumLock': X.Mod2Mask,
                       'CapsLock': X.LockMask,
                       'Mod1': X.Mod1Mask,
                       'Mod2': X.Mod2Mask,
                       'Mod3': X.Mod3Mask,
                       'Mod4': X.Mod4Mask,
                       'Mod5': X.Mod5Mask,
                      }

    __KEYCODES = {}

    __WM_TYPE = None

    def __init__(self, win_id=None):
        """
        `win_id`
          id of the window to be created, if no id assume 
          it's Window Manager (root window).
        """
        self.__root = self.__DISPLAY.screen().root
        self._root_id = self.__root.id
        if win_id and win_id != self.__root.id:
            # Normal window
            self._win = self.__DISPLAY.create_resource_object('window', win_id)
            self.id = win_id
        else:
            # WindowManager, act as root window
            self._win = self.__root 
            self.id = self._win.id

    @classmethod
    def set_wm_type(cls, wm_type):
        """Set window manager's type.
        
        This method should not be called directly. 
        Use :meth:`~pywo.core.windows.WindowManager.update_type` instead.
        
        """
        cls.__WM_TYPE = wm_type

    @property
    def wm_type(self):
        """Return tuple of window manager's type(s)."""
        return CustomTuple([self.__WM_TYPE])

    @classmethod
    def atom(cls, name):
        """Return atom with given name."""
        return cls.__DISPLAY.intern_atom(name)

    @classmethod
    def atom_name(cls, atom):
        """Return atom's name."""
        return cls.__DISPLAY.get_atom_name(atom)

    def get_property(self, name):
        """Return property (``None`` if there's no such property)."""
        atom = self.atom(name)
        property = self._win.get_full_property(atom, 0)
        return property

    def send_event(self, data, event_type, mask):
        """Send event to the root window."""
        event = ClientMessage(
                    window=self._win,
                    client_type=event_type,
                    data=(32, (data)))
        self.__root.send_event(event, event_mask=mask)

    def register(self, event_handler):
        """Register new event handler and update event mask."""
        masks = self.__EVENT_DISPATCHER.register(self, event_handler)
        self.__set_event_mask(masks)

    def unregister(self, event_handler=None):
        """Unregister event handler(s) and update event mask.
        
        If event_handler is ``None`` all handlers will be unregistered.

        """
        masks = self.__EVENT_DISPATCHER.unregister(self, event_handler)
        self.__set_event_mask(masks)

    def _unregister_all(self):
        """Unregister all event handlers for all windows."""
        masks = self.__EVENT_DISPATCHER.unregister()
        # TODO: this will set event mask only on root window!
        self.__set_event_mask(masks)

    def __set_event_mask(self, masks):
        """Update event mask."""
        event_mask = 0
        log.debug('Setting %s masks for %s' % 
                  ([str(e) for e in masks], self))
        for mask in masks:
            event_mask = event_mask | mask
        self._win.change_attributes(event_mask=event_mask)

    def __grab_key(self, keycode, modifiers):
        """Grab key."""
        self._win.grab_key(keycode, modifiers, 
                           1, X.GrabModeAsync, X.GrabModeAsync,
                           onerror=self.__BAD_ACCESS)
        self.sync()
        if self.__BAD_ACCESS.get_error():
            log.error("Can't use %s" % self.keycode2str(modifiers, keycode))

    def grab_key(self, modifiers, keycode, numlock, capslock):
        """Grab key.

        Grab key alone, with CapsLock on and/or with NumLock on.

        """
        if numlock in [0, 2] and capslock in [0, 2]:
            self.__grab_key(keycode, modifiers)
        if numlock in [0, 2] and capslock in [1, 2]:
            self.__grab_key(keycode, modifiers | X.LockMask)
        if numlock in [1, 2] and capslock in [0, 2]:
            self.__grab_key(keycode, modifiers | X.Mod2Mask)
        if numlock in [1, 2] and capslock in [1, 2]:
            self.__grab_key(keycode, modifiers | X.LockMask | X.Mod2Mask)

    def ungrab_key(self, modifiers, keycode, numlock, capslock):
        """Ungrab key.

        Ungrab key alone, with CapsLock on and/or with NumLock on.

        """
        if numlock in [0, 2] and capslock in [0, 2]:
            self._win.ungrab_key(keycode, modifiers)
        if numlock in [0, 2] and capslock in [1, 2]:
            self._win.ungrab_key(keycode, modifiers | X.LockMask)
        if numlock in [1, 2] and capslock in [0, 2]:
            self._win.ungrab_key(keycode, modifiers | X.Mod2Mask)
        if numlock in [1, 2] and capslock in [1, 2]:
            self._win.ungrab_key(keycode, modifiers | X.LockMask | X.Mod2Mask)

    def _translate_coords(self, x, y):
        """Return translated coordinates.
        
        Untranslated coordinates are relative to window.
        Translated coordinates are relative to :ref:`viewport`.

        """
        return self._win.translate_coords(self.__root, x, y)

    @classmethod
    def str2modifiers(cls, masks, splitted=False):
        """Parse modifiers."""
        if not splitted:
            masks = masks.split('-')
        modifiers = 0
        for mask in masks:
            if not mask:
                continue
            mask = mask.capitalize()
            if mask not in cls.__KEY_MODIFIERS.keys():
                raise ValueError('Invalid modifier: %s' % mask)
            modifiers = modifiers | cls.__KEY_MODIFIERS[mask]

        return modifiers or X.AnyModifier

    @classmethod
    def str2keycode(cls, key):
        """Parse keycode."""
        keysym = XK.string_to_keysym(key)
        keycode = cls.__DISPLAY.keysym_to_keycode(keysym)
        cls.__KEYCODES[keycode] = key
        if keycode == 0:
            raise ValueError('No key specified!')
        return keycode

    @classmethod
    def str2modifiers_keycode(cls, code, key=''):
        """Convert `code`, `key` as string(s) into (modifiers, keycode) pair.
        
        There must be both modifier(s) and key persent. If you send both
        modifier(s) and key in one string, they must be separated using '-'. 
        Modifiers must be separated using '-'.

        Keys are case insensitive.

        If you want to use upper case use Shift modifier.
        Only modifiers defined in __KEY_MODIFIERS are valid.
        For example: "Ctrl-A", "Super-Alt-x"
        
        """
        if key:
            code = '-'.join([code, key])
        code = code.split('-')
        key = code[-1]
        masks = code[:-1]
        
        modifiers = cls.str2modifiers(masks, True)
        keycode = cls.str2keycode(key)
        return (modifiers, keycode)

    @classmethod
    def keycode2str(cls, modifiers, keycode):
        """Convert `modifiers`, `keycode` pair into string.
        
        .. note::
            Works ONLY for already registered keycodes!
        
        """
        key = []
        for name, code in cls.__KEY_MODIFIERS.items():
            if modifiers & code:
                key.append(name)

        key.append(cls.__KEYCODES[keycode])
        return '-'.join(key)

    # TODO: check other XINERAMA methods
    @classmethod
    def has_extension(cls, extension):
        """Return True if given extension is available."""
        return cls.__DISPLAY.has_extension(extension)

    @classmethod
    def has_xinerama(cls):
        """Return ``True`` if the Xinerama extension is available."""
        return cls.has_extension('XINERAMA')

    @classmethod
    def has_shape(cls):
        """Return ``True`` if the SHAPE extension is available."""
        return cls.has_extension('SHAPE')

    @classmethod
    def screen_geometries(cls):
        """Return list of :ref:`screen` :class:`~pywo.core.basic.Geometry`. 
        
        If Xinerama extension is not avaialbe fallback to non-Xinerama.
        
        """
        try:
            geometries = []
            for screen in cls.__DISPLAY.xinerama_query_screens().screens:
                geometries.append(Geometry(screen.x, screen.y,
                                           screen.width, screen.height))
            return geometries
        except AttributeError:
            root = cls.__DISPLAY.root
            return [Geometry(0, 0, root.screen_width, root.screen_height)]

    def draw_rectangle(self, x, y, width, height, line):
        """Draw simple rectangle on screen.
        
        .. note:
          OBSOLETE! Use osd_rectangle instead!
        
        """
        color = self.__DISPLAY.screen().black_pixel
        gc = self.__root.create_gc(line_width=line,
                                   join_style=X.JoinRound,
                                   foreground=color,
                                   function=X.GXinvert,
                                   subwindow_mode=X.IncludeInferiors,)
        self.__root.rectangle(gc, x, y, width, height)

    def osd_rectangle(self, geometry, color_name, line_width):
        """Return :class:`OSDRectangle` instance."""
        if not self.has_shape():
            # NOTE: I believe that (almost) all modern window managers
            #       support SHAPE Extension
            return
        color_map = self.__DISPLAY.screen().default_colormap
        color = color_map.alloc_named_color(color_name)
        return OSDRectangle(self.__DISPLAY, geometry, color, line_width)

    def scroll_lock_led(self, on):
        """Turn on/off ScrollLock LED."""
        if on:
            led_mode = X.LedModeOn
        else:
            led_mode = X.LedModeOff
        self.__DISPLAY.change_keyboard_control(led=3, led_mode=led_mode)

    @classmethod
    def flush(cls):
        """Flush request queue to X Server."""
        cls.__DISPLAY.flush()

    @classmethod
    def sync(cls):
        """Flush request queue to X Server, wait until server processes them."""
        cls.__DISPLAY.sync()


class OSDRectangle(object):

    """On Screen Display rectangle using SHAPE X Extenstion."""

    def __init__(self, display, geometry, color, line_width):
        self.display = display
        screen = self.display.screen()
        self.window = screen.root.create_window(geometry.x, geometry.y,
                                                geometry.width, geometry.height,
                                                0, screen.root_depth,
                                                X.InputOutput, X.CopyFromParent,
                                                background_pixel=color.pixel,
                                                override_redirect=True)
        pixmap = self.window.create_pixmap(geometry.width, geometry.height, 1)
        gc = pixmap.create_gc(foreground=0, background=0,
                              join_style=X.JoinRound, line_width=line_width)
        pixmap.fill_rectangle(gc, 0, 0, geometry.width, geometry.height)
        gc.change(foreground=1)
        pixmap.rectangle(gc, line_width / 2, line_width / 2,
                         geometry.width - line_width, 
                         geometry.height - line_width)
        gc.free()
        self.window.shape_mask(shape.ShapeSet, shape.ShapeBounding, 
                               0, 0, pixmap) 

    def show(self):
        """Map `OSDRectangle` window."""
        self.window.map()
        self.display.flush()

    def close(self):
        """Unmap and destroy `OSDRectangle` window."""
        self.window.unmap()
        self.window.destroy()
        self.display.flush()

    def blink(self, duration):
        """Show `OSDRectangle` window, and close after given `duration`."""
        self.show()
        time.sleep(duration)
        self.close()

