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

"""On Screen Display."""

import logging
import time

from Xlib import X
from Xlib.ext import shape


__author__ = "Wojciech 'KosciaK' Pietrzok, Antti Kaihola"


log = logging.getLogger(__name__)


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

        # NOTE: Fix for xlib.ext.shape after refactoring
        if hasattr(shape, 'ShapeSet'):
            shape_set = shape.ShapeSet
        elif hasattr(shape, 'SO'):
            shape_set = shape.SO.Set
        if hasattr(shape, 'ShapeBounding'):
            shape_bounding = shape.ShapeBounding
        elif hasattr(shape, 'SO'):
            shape_bounding = shape.SK.Bounding
        self.window.shape_mask(shape_set, shape_bounding, 
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

