#!/usr/bin/python
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
# 


import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
# Includes webmin and capifaxwm
from capimin_formlib import * 
import cs_helpers,cgi, time, fcntl



capifaxwm.SwitchAndLoadConifg()

header_shown=0
def local_header():
    global header_shown
    if header_shown==1:
        return
    webmin.header("Capisuite - change job (3rd Version)",  config=None, nomodule=1)
    print "<hr><br>"
    header_shown=1


   
try:
    local_header()
    capifaxwm.capiconfig_init()
    # get the "POST" vars
    form = cgi.FieldStorage()
    user = webmin.remote_user

    if form.has_key("change") or form.has_key("schange"):
        if not form.has_key("cindex"):
            raise "NoneSelected"        
        FormChangeJob(user,form)
    else:
        raise capifaxwm.CSInternalError("Unsupport action option")
#    webmin.redirect()
 

except capifaxwm.CSConfigError:
    local_header()
    print "<p><b>%s: False settings/config - please start from the main module page<br>"\
          "and try not to call this page directly</b></p>" % webmin.text.get('error','').upper()
except capifaxwm.CSInternalError,err:
    local_header()
    print "<p><b>%s: Internal error (e.g. function called with wrong params): %s</b></p>" %\
          (webmin.text.get('error','').upper(),err)
except capifaxwm.CSRemoveError,e:
    local_header()
    print "<p><b>%s: %s</b></p>" %(webmin.text.get('error','').upper(),cgi.escape(e.message,1))
except "NoAccess":
    local_header()
    print "<p><b> Sorry, you don't have the permisson for removing/changing the job<br>"\
          "Ask your (Usermin) Admin about it</b></p>"
except capifaxwm.CSUserInputError,err:
    local_header()
    print "<p><b>%s: Invalid Formvalue(s): %s</b></p>" % (webmin.text.get('error','').upper(),err)
except capifaxwm.CSJobChangeError,err:
    local_header()
    print "<p><b>%s: Failed to change the job: %s</b></p>" % (webmin.text.get('error','').upper(),err)
except "NoneSelected":
    local_header()
    print "<p><b> No job selected</b></p>"

if header_shown==1:
    print "<br><hr>"
    webmin.footer([("", "module index")])
