#!/usr/bin/python
# -*-Python-*-
# usermin
import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
import webmin
import capifaxwm
import cs_helpers,os, re,getopt, cgi, time, fcntl

webmin.header("Capisuitefax - change fax", config=1, nomodule=1)
print "<hr>"

try:
    capifaxwm.capiconfig_init()
    # get the "POST" vars
    form = cgi.FieldStorage()
    user = webmin.remote_user
    if (not form) or (capifaxwm.checkconfig() == -1) or (capifaxwm.checkfaxuser(user,1) == 0):
	raise capifaxwm.CSConfigError
    formTime = form.getfirst("year")+"-"+form.getfirst("month")+"-"+form.getfirst("day")+" "+\
		form.getfirst("hour")+":"+form.getfirst("min")
    
#    print "<p> Date:"+formTime+"</p>"
    try:
        timestruct = time.strptime(formTime,"%Y-%m-%d %H:%M")
	timec = time.asctime(timestruct)
    except:
	print "<p> Invalid time and/or date </p>"
	raise capifaxwm.CSConfigError
#    print "<p> ASCTime: "+timec+"</p>"
#    print "<p> %s %s %s %s <br> " % (form.getfirst("formFaxID"),form.getfirst("formDialString"),form.getfirst("formDialAddressee"),form.getfirst("formTries"))
#    print " %s %s </p>" % (form.getfirst("formOrgDate"),form.getfirst("formSubject"))
    
    # check post values
    
    if (not form.getfirst("formFaxID")) or (not form.getfirst("formDialString")) or (not form.getfirst("formOrgDate"))	or (not form.getfirst("formTries")):
        raise capifaxwm.CSConfigError
    
    subject = ""
    addressee = ""
    if form.getfirst("formSubject"):
	subject = form.getfirst("formSubject")
    if form.getfirst("formDialAddressee"):
	addressee = form.getfirst("formDialAddressee")
    dialstring = form.getfirst("formDialString")
    tries = form.getfirst("formTries")
    faxid = form.getfirst("formFaxID")
    if capifaxwm.CheckJobID(faxid)==-1:
	# this should never happen...
	print "<p><b> CRITICAL ERROR: False data in fax ID - check the module/source code! </b></p>"
	raise capifaxwm.CSConfigError
    
    sendq=os.path.join(capifaxwm.UsersFax_Path,user,"sendq")+os.sep
    if (not os.access(sendq,os.W_OK)):
            print "<p>can't write to queue dir</p>"
	    raise capifaxwm.CSConfigError # might be better to use s.th. else ...
    
    jobfile = sendq+"fax-"+faxid+".txt"
    try:
	lockfile=open(jobfile[:-3]+"lock","w")
	# lock so that it isn't deleted while sending
	fcntl.lockf(lockfile,fcntl.LOCK_EX | fcntl.LOCK_NB)
	cs_helpers.writeDescription(jobfile[:-3]+"sff","dialstring=\""+dialstring+"\"\n"
	  +"starttime=\""+timec+"\"\ntries=\""+tries+"\"\n"
	  +"user=\""+user+"\"\naddressee=\""+addressee+"\"\nsubject=\""
	  +subject+"\"\n")
	fcntl.lockf(lockfile,fcntl.LOCK_UN)
	os.unlink(jobfile[:-3]+"lock")
    except IOError,err:
	if (err.errno in (errno.EACCES,errno.EAGAIN)):
	    print "<p><b>Job is currently in transmission. Can't abort.</b></p>"
    print '<p><b> Fax to %s %s (with ID %s) changed</b></p>' % (addressee,dialstring,faxid)

except capifaxwm.CSConfigError:
    print "<p><b>ERROR: False settings/config - please start from the main module page<br> and try not to call this page directly</b></p>"
print "<hr>"
webmin.footer([("", "module index")])
