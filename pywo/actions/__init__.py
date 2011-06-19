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

"""PyWO actions related code.

Actions change windows or window manager state.

PyWO uses pkg_resources for actions plugins discovery. 
When writing your own actions please use 'pywo.actions' entry point group, 
and use module name as an value for entry point. 
Check /examples/plugins/actions for an example of third-party actions plugin.

"""

import logging

from pywo.actions.core import TYPE_FILTER, STATE_FILTER, TYPE_STATE_FILTER
from pywo.actions.core import ActionException, Action
from pywo.actions.core import register, perform, get_current_workarea
from pywo.actions import manager


__author__ = "Wojciech 'KosciaK' Pietrzok"


log = logging.getLogger(__name__)

