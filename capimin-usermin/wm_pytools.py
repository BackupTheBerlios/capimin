# forward a fax: import the data from a queue file and show a form to enter a new destination
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
# http://capimin.berlios.de email: cibi@users.berlios.de

import string

def ExtractFloatConfig(configtext,default=None,fmin=None,fmax=None):
    if not configtext or configtext=="": return default
    try:
	fval = float(configtext)
	if fmin and fval<fmin:
	    return default
	if fmax and fval>fmax:
	    return default
    except:
	return default
    return fval
