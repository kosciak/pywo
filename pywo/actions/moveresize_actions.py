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

"""moveresize_actions.py - PyWO actions - moving and resizing windows."""

import logging

from pywo.actions import register, get_current_workarea, TYPE_STATE_FILTER
from pywo.actions.manipulate import Expander, Shrinker, Floater


__author__ = "Wojciech 'KosciaK' Pietrzok"


log = logging.getLogger(__name__)


@register(name='expand', filter=TYPE_STATE_FILTER, unshade=True)
def _expand(win, direction, vertical_first=True, xinerama=False):
    """Expand window in given direction."""
    workarea = get_current_workarea(win, xinerama)
    expand = Expander(workarea=workarea, 
                      adjacent=not direction.is_middle,
                      both_sides=not direction.is_middle,
                      vertical_first=vertical_first)
    geometry = expand(win, direction)
    log.debug('Setting %s' % (geometry,))
    win.set_geometry(geometry, direction)


@register(name='shrink', filter=TYPE_STATE_FILTER, unshade=True)
def _shrink(win, direction, vertical_first=True, xinerama=False):
    """Shrink window in given direction."""
    if direction.is_middle:
        # NOTE: This is not working correctly with is_middle anyway
        return
    workarea = get_current_workarea(win, xinerama)
    shrink = Shrinker(workarea=workarea, 
                      vertical_first=vertical_first)
    geometry = shrink(win, direction.invert())
    log.debug('Setting %s' % (geometry,))
    win.set_geometry(geometry, direction)


@register(name='float', filter=TYPE_STATE_FILTER, unshade=True)
def _move(win, direction, vertical_first=True, xinerama=False):
    """Move window in given direction."""
    workarea = get_current_workarea(win, xinerama)
    expand = Floater(workarea=workarea, 
                     adjacent=not direction.is_middle, 
                     both_sides=not direction.is_middle,
                     vertical_first=vertical_first)
    border = expand(win, direction)
    geometry = win.geometry
    geometry.width = min(border.width, geometry.width)
    geometry.height = min(border.height, geometry.height)
    x = border.x + border.width * direction.x
    y = border.y + border.height * direction.y
    geometry.set_position(x, y, direction)
    log.debug('Setting %s' % (geometry,))
    win.set_geometry(geometry)


@register(name='put', filter=TYPE_STATE_FILTER, unshade=True)
def _put(win, position, gravity=None, xinerama=False):
    """Put window in given position (without resizing)."""
    gravity = gravity or position
    workarea = get_current_workarea(win, xinerama)
    geometry = win.geometry
    x = workarea.x + workarea.width * position.x
    y = workarea.y + workarea.height * position.y
    geometry.set_position(x, y, gravity)
    log.debug('Setting %s' % (geometry,))
    win.set_geometry(geometry)


# TODO: new actions
#   - resize (with gravity?)
#   - move (relative with gravity and +/-length)?
#   - place (absolute x,y)

