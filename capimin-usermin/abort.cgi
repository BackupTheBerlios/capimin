#!/usr/bin/python
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
# http://capimin.berlios.de email: cibi@users.berlios.de


import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
import webmin
import capifaxwm
import cs_helpers,os, re,getopt

webmin.header("Capisuitefax - remove job", config=1, nomodule=1)
print "<hr>"

try:
    # get the "GET" vars
    webmin.ReadParse()
    # open / read the config file and send queue path
    capifaxwm.capiconfig_init()
    if webmin.indata==None:	
	raise capifaxwm.CSConfigError # might be better to use s.th. else ...
    if (not webmin.indata.has_key("jobid")):
	raise capifaxwm.CSConfigError # might be better to use s.th. else ...
    if (not webmin.indata.has_key("qtype")):
	queuetype="faxsend"
    else:
	queuetype = webmin.indata["qtype"].value	
    	
    if capifaxwm.removejob(webmin.remote_user,webmin.indata["jobid"].value,queuetype) != -1:
	print '<p><b> Job with ID %s aborted/deleted </b></p>' %  webmin.indata["jobid"].value
    else:
	print '<p><b> Error while remove job %s, qtype %s </b></p>' % (webmin.indata["jobid"].value,queuetype)
except capifaxwm.CSConfigError:
    print "<p><b>ERROR: False settings/config - please start from the main module page<br> and try not to call this page directly</b></p>"
print "<p>&nbsp;</p><hr>"
webmin.footer([("", "module index")])
