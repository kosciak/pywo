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

"""services - package containing PyWO services related code.

PyWO uses pkg_resources for services plugins discovery. 
When writing your own actions please use 'pywo.services' entry point group. 
As an entry point value you can use Service subclass, or module implementing
setup(config), start(), stop() functions.
Check /examples/plugins/services for an example of third-party services plugin.

"""

import logging

from pywo.services.core import Service


__author__ = "Wojciech 'KosciaK' Pietrzok"


log = logging.getLogger(__name__)

