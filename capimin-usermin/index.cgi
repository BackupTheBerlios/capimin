#!/usr/bin/python
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
# see http://capimin.berlios.de for info,install, requirements, etc email: cibi@users.berlios.de
# Uses the python-webmin module from Peter Åstrand (http://www.cendio.se/~peter/python-webmin)

import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
import webmin
import cs_helpers,capifaxwm,capimin_lists,wm_pytools

capifaxwm.SwitchAndLoadConifg()


webmin.header(webmin.text['index_title'], None, None,capifaxwm._showconfig,1)

sys.stdout.flush()


print "<hr>"
#init capifaxwm module:
if (capifaxwm.capiconfig_init()==-1):
    print "<p><b>%s: Could not read/invalid configuration </b></p>" % webmin.text.get('error','').upper()
elif (capifaxwm.checkfaxuser(webmin.remote_user)==0):
    print '<p><b>%s: user "%s" is not a valid capisuite fax user<br> Your Webmin/Usermin name must match a capisuite fax user (= *nix user) </b></p>' % (webmin.text.get('error','').upper(),webmin.remote_user)
else:
    print '<form action="newfax.cgi" method="POST"><input type="hidden" name="faxcreate" value="new"><input type=SUBMIT value="Newfax"></form>'
    print '\n<hr>\n'

    remove_gdirs = wm_pytools.ExtractIntConfig(webmin.config.get('remove_gdirs'),0,0,1)
    gremovepage=None
    if remove_gdirs == 1:
	gremovepage="abort.cgi"
    
    if not capifaxwm._OldWebminpy and webmin.userconfig:
	show_lists = webmin.userconfig.get('show_list',[0,1,2,3,4]).split(',',5)
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
	    capimin_lists.ShowGlobal(webmin.remote_user,"faxdone",removepage=gremovepage)	    
	elif l==4:
	    print "<p><b> Failed List: Fax</b></p>"
	    capimin_lists.ShowGlobal(webmin.remote_user,"faxfailed",removepage=gremovepage)	
	else:
	    print "<p> Invalid show_list option or list or queue unknown - listening stopped </p>"
	    break

print "<p>&nbsp;</p><hr>"		
webmin.footer([("/", "index")])

