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
cslist = None

header_shown=0
def local_header():
    global header_shown
    if header_shown==1:
        return
    webmin.header("Capisuite - change job",  config=None, nomodule=1)
    print "<hr><br>"
    header_shown=1


def show_askform(formjoblist,actionpage="delete.cgi",returnpage="index.cgi"):
    # raise CSInternalError, the checks are and should be done befere this function is called
    # (e.g. to give the user a better error message)
    if not formjoblist:
        raise capifaxwm.CSInternalError("show_askform()")
    if not isinstance(formjoblist, list):
        raise capifaxwm.CSInternalError("show_askform()")

    local_header()
        
    print '<table border="1">'
    print ' <tr bgcolor=#%s><th>&nbsp;&nbsp;&nbsp;Remove (delete/abort) %s job(s) ?&nbsp;&nbsp;&nbsp;</th></tr>  ' % (webmin.tb,len(formjoblist))
    print ' <tr bgcolor=#%s><td>' % webmin.cb
    print '   <table cellpadding="10" cellspacing="2" width="100%">\n    <tr>'
    print ' <td align="center"><form method="POST" action="delete.cgi"><input type="submit" value="Yes" name="rmyes">'
    for cjob in formjoblist:
        print '     <input type="hidden" name="cjobid" value=%s>' % cjob
    print '     <input type="hidden" name="cslist" value="%s"></form></td>' % cslist
    print ' <td align="center"><form method="POST" action="index.cgi"><input type="submit" value="No" name="rmno"></form></td>'
    print '   </tr></table></td></tr>\n</table>'

def remove_jobs(formjoblist):    
    # raise CSInternalError, the checks are and should be done befere this function is called
    # (e.g. to give the user a better error message)
    if not formjoblist:
        raise capifaxwm.CSInternalError("remove_jobs()")
    if not isinstance(formjoblist, list):
        formjoblist = [formjoblist] # ;)

    for cjob in formjoblist:
        try:
            capifaxwm.removejob(webmin.remote_user,cjob,cslist)    
        except capifaxwm.CSRemoveError,e:
            local_header()
            print "<br><b>%s: %s - JobID: %s </b><br>" %(webmin.text.get('error','').upper(),cgi.escape(e.message,1),cjob)
    if header_shown==0:
        webmin.redirect()

try:
    # get the cgi data
    formdata = cgi.FieldStorage()
    if not formdata or (not formdata.has_key("cslist")):
        raise capifaxwm.CSConfigError # might be better to use s.th. else ...
    cslist = formdata.getfirst("cslist")
    remove_gdirs = wm_pytools.ExtractIntConfig(webmin.config.get('remove_gdirs'),0,0,1)

    if remove_gdirs!=1 and (cslist=="faxdone" or cslist=="faxfailed"):
        raise "NoAccess"
    elif cslist!="faxdone" and cslist!="faxfailed":
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
    local_header()
    print "<p><b>%s: %s</b></p>" %(webmin.text.get('error','').upper(),cgi.escape(e.message,1))
except "NoAccess":
    local_header()
    print "<p><b> Sorry, you don't have the permisson for removing the job<br> Ask your (Usermin) Admin about it</b></p>"
except "NoneSelected":
    local_header()
    print "<p><b> No job selected</b></p>"
except capifaxwm.CSConfigError:
    local_header()
    print "<p><b> %s: False settings/config - please start from the main module page<br> and try not to call this page directly</b></p>" % webmin.text.get('error','').upper()
except capifaxwm.CSInternalError,e:
    local_header()
    print "<p><b>Internal Error: %s</b></p>" %(cgi.escape(e.message,1))

if header_shown==1:
    print "<p>&nbsp;</p><hr>"
    webmin.footer([("", "module index")])
