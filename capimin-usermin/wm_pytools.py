#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
# http://capimin.berlios.de email: cibi@users.berlios.de

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
