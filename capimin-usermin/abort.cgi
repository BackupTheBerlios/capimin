#!/usr/bin/python
#
# remove a job (deleting the jobfiles)
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
# http://capimin.berlios.de email: cibi@users.berlios.de


import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
import webmin
import cs_helpers,capifaxwm
import cgi

webmin.header("Capisuitefax - remove job", config=None, nomodule=1)
print "<hr>"

try:
    capifaxwm.capiconfig_init()
    # get the cgi data
    formdata = cgi.FieldStorage()
    # basic cgi data check
    if not formdata: 
	raise capifaxwm.CSConfigError    
    if not formdata.has_key("jobid"):
	raise capifaxwm.CSConfigError # might be better to use s.th. else ...
    if not formdata.has_key("qtype"):
	raise capifaxwm.CSConfigError # might be better to use s.th. else ...
    
    if capifaxwm.removejob(webmin.remote_user,formdata.getfirst("jobid"),formdata.getfirst("qtype")) != -1:
	print '<p><b> Job with ID %s removed </b></p>' %  formdata.getfirst("jobid")
    else:
	print '<p><b> %s while removing job %s, qtype %s </b></p>' % (webmin.text.get('error','').upper(),formdata.getfirst("jobid"),formdata.getfirst("qtype"))
except capifaxwm.CSConfigError:
    print "<p><b> %s: False settings/config - please start from the main module page<br> and try not to call this page directly</b></p>" % webmin.text.get('error','').upper()
print "<p>&nbsp;</p><hr>"
webmin.footer([("", "module index")])
