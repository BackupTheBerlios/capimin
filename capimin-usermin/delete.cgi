#!/usr/bin/python
#
# remove multiple jobs (deleting the jobfiles)
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

def show_askform(fromjoblist):
    # raise CSInternalError, the checks are and should be done befere this function is called
    # (e.g. to give the user a better error message)
    if not fromjoblist:
        raise capifaxwm.CSInternalError("show_askform()")
    if not isinstance(fromjoblist, list):
        raise capifaxwm.CSInternalError("show_askform()")
    webmin.header("Capisuitefax - remove job(s)", config=None, nomodule=1)
    print "<hr><br>"
    
    print '<table border="1">'
    print ' <tr bgcolor=#%s><th>&nbsp;&nbsp;&nbsp;Remove (delete/abort) %s job(s) ?&nbsp;&nbsp;&nbsp;</th></tr>  ' % (webmin.tb,len(fromjoblist))
    print ' <tr bgcolor=#%s><td>' % webmin.cb
    print '   <table cellpadding="10" cellspacing="2" width="100%">\n    <tr>'
    print ' <td align="center"><form method="POST" action="delete.cgi"><input type="submit" value="Yes" name="rmyes">'
    for cjob in fromjoblist:
        print '     <input type="hidden" name="cjobid" value=%s>' % cjob
    print '     <input type="hidden" name="qtype" value="%s"></form></td>' % qtype
    print ' <td align="center"><form method="POST" action="index.cgi"><input type="submit" value="No" name="rmno"></form></td>'
    print '   </tr></table></td></tr>\n</table>'

def remove_jobs(fromjoblist):    
    # raise CSInternalError, the checks are and should be done befere this function is called
    # (e.g. to give the user a better error message)
    if not fromjoblist:
        raise capifaxwm.CSInternalError("remove_jobs()")
    if not isinstance(fromjoblist, list):
        raise capifaxwm.CSInternalError("remove_jobs()")

    webmin.header("Capisuitefax - remove job", config=None, nomodule=1,header='<meta http-equiv="refresh" content="20; URL=index.cgi">')
    print "<hr><p>"
    for cjob in fromjoblist:
        try:
            capifaxwm.removejob(webmin.remote_user,cjob,qtype)    
            print '<b> Job with ID %s removed </b><br>' % cjob
        except capifaxwm.CSRemoveError,e:
            print "<br><b>%s: %s - JobID: %s </b><br>" %(webmin.text.get('error','').upper(),cgi.escape(e.message,1),cjob)
    print '</p><p><i> Returning to index page in 20 seconds...</i></p>'                   

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
        raise capifaxwm.CSInternalError("no form data")    
    
    if not formdata.has_key("cjobid"):
        raise "NoneSelected"
       
    if webmin.userconfig:
        ask_before_rm = wm_pytools.ExtractIntConfig(webmin.userconfig.get('remove_ask'),1,0,1)
    if ask_before_rm==0 or formdata.has_key("rmyes"):
        remove_jobs(formdata.getlist("cjobid"))
    else:
        show_askform(formdata.getlist("cjobid"))
    
    
except capifaxwm.CSRemoveError,e:
    webmin.header("Capisuitefax - remove job", config=None, nomodule=1)
    print "<hr><br>"
    print "<p><b>%s: %s</b></p>" %(webmin.text.get('error','').upper(),cgi.escape(e.message,1))
except "NoAccess":
    webmin.header("Capisuitefax - remove job", config=None, nomodule=1)
    print "<hr><br>"
    print "<p><b> Sorry, you don't have the permisson for removing the job<br> Ask your (Usermin) Admin about it</b></p>"
except "NoneSelected":
    webmin.header("Capisuitefax - remove job", config=None, nomodule=1)
    print "<hr><br>"
    print "<p><b> No job selected</b></p>"
except capifaxwm.CSConfigError:
    webmin.header("Capisuitefax - remove job", config=None, nomodule=1)
    print "<hr><br>"
    print "<p><b> %s: False settings/config - please start from the main module page<br> and try not to call this page directly</b></p>" % webmin.text.get('error','').upper()
except capifaxwm.CSInternalError,e:
    webmin.header("Capisuitefax - remove job", config=None, nomodule=1)
    print "<hr><br>"
    print "<p><b>Internal Error: %s</b></p>" %(cgi.escape(e.message,1))
print "<p>&nbsp;</p><hr>"
webmin.footer([("", "module index")])
