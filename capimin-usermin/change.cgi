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
import cs_helpers,cgi, time, fcntl

capifaxwm.SwitchAndLoadConifg()

header_shown=0
def local_header():
    global header_shown
    if header_shown==1:
        return
    webmin.header("Capisuite - change job",  config=None, nomodule=1)
    print "<hr><br>"
    header_shown=1


    
def FormTimeToCSTime(formtime):
    """Convert time provided (e.g.) by a form to the CapiSuite format
        formtime sample "2005-1-29 2:21"
        return value is genderated by time.asctime(..) sample: "Sat Jan 29 02:21:00 2005"
            which is used by capisuite in the jobfiles
    """
    try:
        timestruct = time.strptime(formtime,"%Y-%m-%d %H:%M")
        cstime = time.asctime(timestruct)
    except:
        raise capifaxwm.CSUserInputError("Invalid time and/or date from Formdata")
    return cstime
    
def form_changejob(user,formdata):
    if (not form) or (capifaxwm.checkconfig() == -1) or (capifaxwm.checkfaxuser(user,1) == 0):
        raise capifaxwm.CSConfigError
    formTime = formdata.getfirst("year","")+"-"+formdata.getfirst("month","")+"-"+formdata.getfirst("day","")+" "+\
                formdata.getfirst("hour","")+":"+formdata.getfirst("min","")
    jtime=FormTimeToCSTime(formTime)       
    if (not formdata.has_key("jobid")) or (not formdata.has_key("formDialString")) or (not formdata.has_key("formOrgDate")) or (not formdata.has_key("formTries")) or (not form.has_key("filetype")):
        raise capifaxwm.CSConfigError
    subject = form.getfirst("formSubject","")
    addressee = form.getfirst("formDialAddressee","")
    dialstring = form.getfirst("formDialString")
    jtries = form.getfirst("formTries")
    jobid = form.getfirst("jobid")
    filetype = form.getfirst("filetype")
    cslist = form.getfirst("cslist")

    capifaxwm.change_job(user,jobid,cslist,dialstring,filetype,jtime,addressee,subject,jtries)

    
try:
    capifaxwm.capiconfig_init()
    # get the "POST" vars
    form = cgi.FieldStorage()
    user = webmin.remote_user

    form_changejob(user,form)
    webmin.redirect()
 

except capifaxwm.CSConfigError:
    local_header()
    print "<p><b>%s: False settings/config - please start from the main module page<br> and try not to call this page directly</b></p>" % webmin.text.get('error','').upper()
except capifaxwm.CSInternalError,err:
    local_header()
    print "<p><b>%s: Inernal error (e.g. function called with wrong params): %s</b></p>" % (webmin.text.get('error','').upper(),err)
except capifaxwm.CSUserInputError,err:
    local_header()
    print "<p><b>%s: Invalid Formvalue(s): %s</b></p>" % (webmin.text.get('error','').upper(),err)
except capifaxwm.CSJobChangeError,err:
    local_header()
    print "<p><b>%s: Failed to change the job: %s</b></p>" % (webmin.text.get('error','').upper(),err)

if header_shown==1:
    print "<hr>"
    webmin.footer([("", "module index")])
