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

"""High level wrapper around Xlib.

`core` package encapsulates all comunication with X Server.

It contains objects representing Window Manager, Windows, and other basic
concepts needed for repositioning and resizing windows (size, position,
extents, gravity, etc).

"""

import logging

from pywo.core.basic import Gravity, Size, Position, Geometry, Extents, Layout
from pywo.core.enums import WindowType, ManagerType, State, Mode
from pywo.core.windows import Window
from pywo.core.manager import WindowManager


__author__ = "Wojciech 'KosciaK' Pietrzok"


log = logging.getLogger(__name__)

