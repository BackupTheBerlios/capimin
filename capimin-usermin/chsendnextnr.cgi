#!/usr/bin/env python
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
# Coding style: Max linewidth 120 chars, 4 spaces per tab
#




import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
import webmin,capifaxwm,wm_pytools
import cs_helpers,os,pwd,stat


capifaxwm.capiconfig_init()

webmin.header("Capisuitefax - change fax-nextnr ownership in sendq", config=None, nomodule=1)
print "<hr>"
try:
    if webmin.config:
        canchange = wm_pytools.ExtractIntConfig(webmin.config.get('allow_faxnext_chown'),0,0,1)
    else:
        canchange = 0
    if canchange != 1:
        raise "NoAccess","<p><b> Sorry, you are not allowed to chown "+faxnextfile+" in the sendq dir<br>"\
              "Ask your (Usermin) admin for the permission </p></b>"

    qpath=os.path.join(capifaxwm.UsersFax_Path,webmin.remote_user,"sendq")+os.sep

    userstat=pwd.getpwnam(webmin.remote_user)
    if not userstat:
        raise "Error"

    if os.stat(qpath+capifaxwm.faxnextfile)[stat.ST_UID] != userstat[2]:
        os.chown(qpath+capifaxwm.faxnextfile,userstat[2],userstat[3])
        print "<p> permission changed (owner and group)</p>"
    else:
        print "<p> you are already owning the file</p>"

except "NoAccess", emsg:
    print emsg
except:
    print "<p> Error </p>"

print "<hr>"
webmin.footer([("", "module index")])
