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
import wm_pytools



capifaxwm.SwitchAndLoadConifg()

#from capimin_formlib:
LocalHeaderSetup("Capisuite - change job (3rd Version)")
   
try:
    capifaxwm.capiconfig_init()
    # get the "POST" vars
    form = cgi.FieldStorage()
    user = webmin.remote_user
    cslist=""
    if form.has_key("cslist"):
        cslist=form.getfirst("cslist")

    if form.has_key("change") or form.has_key("schange"):
        if not form.has_key("cindex"):
            raise "NoneSelected"        
        FormChangeJob(user,form)
        if not IsHeaderShown():
            webmin.redirect()
    elif form.has_key("delete"):
        if not form.has_key("cindex"):
            raise "NoneSelected"  
        if cslist=="faxdone" and cslist=="faxfailed":
            raise capifaxwm.CSInternalError("Can't remove jobs/files from global lists with this cgi file")
        if webmin.userconfig:
            ask_before_rm = wm_pytools.ExtractIntConfig(webmin.userconfig.get('remove_ask'),1,0,1)
        if ask_before_rm==0 or form.has_key("rmyes"):            
            FormRemoveJobs(webmin.remote_user,form)
            if not IsHeaderShown():
                webmin.redirect()
        else:
            LocalHeader()
            ShowForm_RemoveAsk(form,"change.cgi")        

    else:
        raise capifaxwm.CSInternalError("Unsupport action option")

 

except capifaxwm.CSConfigError:
    LocalHeader()
    print "<p><b>%s: False settings/config - please start from the main module page<br>"\
          "and try not to call this page directly</b></p>" % webmin.text.get('error','').upper()
except capifaxwm.CSInternalError,err:
    LocalHeader()
    print "<p><b>%s: Internal error (e.g. function called with wrong params): %s</b></p>" %\
          (webmin.text.get('error','').upper(),err)
except capifaxwm.CSRemoveError,e:
    LocalHeader()
    print "<p><b>%s: %s</b></p>" %(webmin.text.get('error','').upper(),cgi.escape(e.message,1))
except "NoAccess":
    LocalHeader()
    print "<p><b> Sorry, you don't have the permisson for removing/changing the job<br>"\
          "Ask your (Usermin) Admin about it</b></p>"
except capifaxwm.CSUserInputError,err:
    LocalHeader()
    print "<p><b>%s: Invalid Formvalue(s): %s</b></p>" % (webmin.text.get('error','').upper(),err)
except capifaxwm.CSJobChangeError,err:
    LocalHeader()
    print "<p><b>%s: %s: %s</b></p>" % (webmin.text.get('error','').upper(),webmin.text.get('change_job_error',''),err)
except "NoneSelected":
    LocalHeader()
    print "<p><b> No job selected<br>(if you use the browser back button, the form usually still holds your changes)</b></p>"

if IsHeaderShown():
    print "<br><hr>"
    webmin.footer([("", "module index")])
