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

webmin.init_config()
# -----------------
# needed, because the current webmin.py does not contain create_user_config_dirs and userconfig
OldWebminpy=None
showconfig=1
try:
    webmin.create_user_config_dirs()
except NotImplementedError:
    OldWebminpy=1
    showconfig=None
# -----------------
webmin.header(webmin.text['index_title'], None, None,showconfig,1)

sys.stdout.flush()


print "<hr>"
#init capifaxwm module:
if (capifaxwm.capiconfig_init()==-1):
    print "<p><b>%s: Could not read/invalid configuration </b></p>" % webmin.text['error'].upper()
elif (capifaxwm.checkfaxuser(webmin.remote_user)==0):
    print '<p><b>%s: user "%s" is not a valid capisuite fax user<br> Your Webmin/Usermin name must match a capisuite fax user (= *nix user) </b></p>' % (webmin.text['error'].upper(),webmin.remote_user)
else:

    print '<form action="newfax.cgi" method="POST"><input type="hidden" name="faxcreate" value="new"><input type=SUBMIT value="Newfax"></form>'
    
    print '\n<hr>\n'
    if not OldWebminpy and webmin.userconfig.has_key('show_list'):
	show_lists = webmin.userconfig['show_list'].split(',',5)	
    else:
	show_lists = [0,1,2,3,4]

    for ls in show_lists:
	l=int(ls)
	if l==0:
	     print "<p><b> Send Queue</b></p>"
	     capimin_lists.ShowSend(webmin.remote_user)
	elif l==1:
	    print "<p><b> Received List: Fax</b></p>"
	    capimin_lists.ShowReceived(webmin.remote_user,forwardopt=1,dldpage="download.cgi",removepage="abort.cgi")
	elif l==2 and capifaxwm.checkconfig("voice")!=-1:
	    print "<p><b> Received List: Voice</b></p>"
	    capimin_lists.ShowReceived(webmin.remote_user,fileprefix="voice",dldpage="download.cgi",removepage="abort.cgi")
	elif l==3:
	    print "<p><b> Done List: Fax</b></p>"
	    capimin_lists.ShowGlobal(webmin.remote_user,"faxdone","abort.cgi")	    
	elif l==4:
	    print "<p><b> Failed List: Fax</b></p>"
	    capimin_lists.ShowGlobal(webmin.remote_user,"faxfailed","abort.cgi")	
	else:
	    print "<p> Invalid show_list option or list or queue unknown - listening stopped </p>"
	    break

print "<p>&nbsp;</p><hr>"		
webmin.footer([("/", "index")])
#print "</body></html>"
