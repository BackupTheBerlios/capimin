#!/usr/bin/python
#
# chsendnextnr.cgi - change the permission if the fax-nextnr in the
# user sendq dir
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
# http://capimin.berlios.de email: cibi@users.berlios.de


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
	raise "NoAccess","<p><b> Sorry, you are not allowed to chown "+faxnextfile+" in the sendq dir<br>Ask your (Usermin) admin for the permission </p></b>"

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
