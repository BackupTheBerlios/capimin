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
import capifaxwm,capimin_lists
import cs_helpers,os, re,getopt

webmin.header(webmin.text['index_title'], None, None,0,1)

sys.stdout.flush()
webmin.init_config()

print "<hr>"
#init capifaxwm module:
if (capifaxwm.capiconfig_init()==-1):
    print "<p><b>%s: Could not read/invalid configuration </b></p>" % webmin.text['error'].upper()
elif (capifaxwm.checkfaxuser(webmin.remote_user)==0):
    print '<p><b>%s: user "%s" is not a valid capisuite fax user<br> Your Webmin/Usermin name must match a capisuite fax user (= *nix user) </b></p>' % (webmin.text['error'].upper(),webmin.remote_user)
else:
    print '<form action="newfax.cgi" method="POST"><input type="hidden" name="faxcreate" value="new"><input type=SUBMIT value="Newfax"></form>'
    print "<hr>\n<p><b> Send Queue</b></p>"
    capimin_lists.ShowSend(webmin.remote_user)
    print "<p><b> Received List: Fax</b></p>"
    capimin_lists.ShowReceived(webmin.remote_user,forwardopt=1,dldpage="download.cgi",removepage="abort.cgi")
    if capifaxwm.checkconfig("voice")!=-1:
	print "<p><b> Received List: Voice</b></p>"
	capimin_lists.ShowReceived(webmin.remote_user,fileprefix="voice",dldpage="download.cgi",removepage="abort.cgi")
    print "<p><b> Done List: Fax</b></p>"
    capimin_lists.ShowGlobal(webmin.remote_user,"faxdone")
    print "<p><b> Failed List: Fax</b></p>"
    capimin_lists.ShowGlobal(webmin.remote_user,"faxfailed")
    
print "<p>&nbsp;</p><hr>"		
webmin.footer([("/", "index")])
#print "</body></html>"
