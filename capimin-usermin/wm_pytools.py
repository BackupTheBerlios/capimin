#
# Written by Carsten <cibi@users.berlios.de>
# Copyright (C) 2003,2004 Carsten (http://capimin.berlios.de)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License. 
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

#
# Coding style: Max linewidth 120 chars
# 

import string

def ExtractFloatConfig(configtext,default=None,vmin=None,vmax=None):
    if not configtext: return default
    try:
        confval = float(configtext)
        if vmin and confval<vmin:
            return default
        if vmax and confval>vmax:
            return default
    except:
        return default
    return confval

def ExtractIntConfig(configtext,default=None,vmin=None,vmax=None):
    if not configtext: return default
    try:
        confval = int(configtext)
        if vmin and confval<vmin:
            return default
        if vmax and confval>vmax:
            return default
    except:
        return default
    return confval

def ToLong(x):
    """Simple Function to convert param x to long
    can also be used to check. Unlike the python long() function, this doesn't raises an
    exception, it simply return None in case of an error
    """
    
    try:
        valueX = long(x)
    except:
        return None
    return valueX
