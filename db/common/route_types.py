# This file is part of Waymarked Trails
# Copyright (C) 2018 Sarah Hoffmann
#
# This is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

from enum import Enum

class Network(Enum):
    """ Basic types of network levels.
    """
    LOC = 0
    REG = 1
    NAT = 2
    INT = 3

    def __call__(self, importance=0):
        if abs(importance) > 3:
            raise Runtime_error("Network importance must be between -3 and 3")
        return 7 * self.value + 3 + importance

    def max(self):
        return self.__call__(3)

    def min(self):
        return self.__call__(-3)

    @staticmethod
    def from_int(i):
        if i <= Network.LOC.max():
            return Network.LOC
        if i <= Network.REG.max():
            return Network.REG
        if i <= Network.NAT.max():
            return Network.NAT
        if i <= Network.INT.max():
            return Network.INT
        raise ValueError("Integer out of range for Network")

