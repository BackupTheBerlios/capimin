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
import cs_helpers,capifaxwm,wm_pytools
import cgi

ask_before_rm=1
remove_gdirs=0

jobid = None
qtype = None


def show_askform():
    webmin.header("Capisuitefax - remove job", config=None, nomodule=1)
    print "<hr><br>"
    print '<table border="1">' 
    print ' <tr bgcolor=#%s><th>&nbsp;&nbsp;&nbsp;Remove (delete/abort) job %s ?&nbsp;&nbsp;&nbsp;</th></tr>  ' % (webmin.tb,jobid)
    print ' <tr bgcolor=#%s><td>' % webmin.cb
    print '   <table cellpadding="10" cellspacing="2" width="100%">\n    <tr>'
    print '	<td align="center"><form method="POST" action="abort.cgi"><input type="submit" value="Yes" name="rmyes">'
    print '	    <input type="hidden" name="jobid" value="%s"><input type="hidden" name="qtype" value="%s"></form></td>' % (jobid,qtype)
    print '	<td align="center"><form method="POST" action="index.cgi"><input type="submit" value="No" name="rmno"></form></td>'
    print '   </tr></table></td></tr>\n</table>'

def remove_job():    
    capifaxwm.removejob(webmin.remote_user,jobid,qtype)
    webmin.header("Capisuitefax - remove job", config=None, nomodule=1,header='<meta http-equiv="refresh" content="4; URL=index.cgi">')
    print "<hr>"
    print '<p><b> Job with ID %s removed </b></p>' %  jobid
    print '<p><i> Returning to index page in 4 seconds...</i></p>'

try:
    # get the cgi data
    formdata = cgi.FieldStorage()
    if not formdata or (not formdata.has_key("qtype")):
	raise capifaxwm.CSConfigError # might be better to use s.th. else ...
    qtype = formdata.getfirst("qtype")
    remove_gdirs = wm_pytools.ExtractIntConfig(webmin.config.get('remove_gdirs'),0,0,1)

    if remove_gdirs!=1 and (qtype=="faxdone" or qtype=="faxfailed"):
	raise "NoAccess"
    elif qtype!="faxdone" and qtype!="faxfailed":
	capifaxwm.SwitchAndLoadConifg()
    else:
        capifaxwm.load_user_config()

    capifaxwm.capiconfig_init()
    # basic cgi data check
    if not formdata: 
	raise capifaxwm.CSConfigError    
    if not formdata.has_key("jobid"):
	raise capifaxwm.CSConfigError # might be better to use s.th. else ...
    jobid = formdata.getfirst("jobid")
    
    
    if webmin.userconfig:
	ask_before_rm = wm_pytools.ExtractIntConfig(webmin.userconfig.get('remove_ask'),1,0,1)
    if ask_before_rm==0 or formdata.has_key("rmyes"):
	remove_job()
    else:
	show_askform()
	
    
except capifaxwm.CSRemoveError,e:
    webmin.header("Capisuitefax - remove job", config=None, nomodule=1)
    print "<hr><br>"
    print "<p><b>%s: %s</b></p>" %(webmin.text.get('error','').upper(),cgi.escape(e.message,1))
except "NoAccess":
    webmin.header("Capisuitefax - remove job", config=None, nomodule=1)
    print "<hr><br>"
    print "<p><b> Sorry, you don't have the permisson for removing the job<br> Ask your (Usermin) Admin about it</b></p>"
except capifaxwm.CSConfigError:
    webmin.header("Capisuitefax - remove job", config=None, nomodule=1)
    print "<hr><br>"
    print "<p><b> %s: False settings/config - please start from the main module page<br> and try not to call this page directly</b></p>" % webmin.text.get('error','').upper()
print "<p>&nbsp;</p><hr>"
webmin.footer([("", "module index")])
 