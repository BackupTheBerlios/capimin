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
import cs_helpers,os, re, cgi, time, fcntl

capifaxwm.SwitchAndLoadConifg()

webmin.header("Capisuitefax - change fax",  config=None, nomodule=1)
print "<hr>"

try:
	capifaxwm.capiconfig_init()
	# get the "POST" vars
	form = cgi.FieldStorage()
	user = webmin.remote_user
	if (not form) or (capifaxwm.checkconfig() == -1) or (capifaxwm.checkfaxuser(user,1) == 0):
		raise capifaxwm.CSConfigError
	formTime = form.getfirst("year","")+"-"+form.getfirst("month","")+"-"+form.getfirst("day","")+" "+\
				form.getfirst("hour","")+":"+form.getfirst("min","")

	try:
		timestruct = time.strptime(formTime,"%Y-%m-%d %H:%M")
		timec = time.asctime(timestruct)
	except:
		print "<p> Invalid time and/or date </p>"
		raise capifaxwm.CSConfigError
#    print "<p> ASCTime: "+timec+"</p>"
#    print "<p> %s %s %s %s <br> " % (form.getfirst("jobid"),form.getfirst("formDialString"),form.getfirst("formDialAddressee"),form.getfirst("formTries"))
#    print " %s %s </p>" % (form.getfirst("formOrgDate"),form.getfirst("formSubject"))
	
	# check post values
	
	if (not form.has_key("jobid")) or (not form.has_key("formDialString")) or (not form.has_key("formOrgDate")) or (not form.has_key("formTries")) or (not form.has_key("filetype")):
		raise capifaxwm.CSConfigError
	
	subject = form.getfirst("formSubject","")
	addressee = form.getfirst("formDialAddressee","")
	dialstring = form.getfirst("formDialString")
	tries = form.getfirst("formTries")
	jobid = form.getfirst("jobid")
	filetype = form.getfirst("filetype")
	if capifaxwm.CheckJobID(jobid)==-1:
		# this should never happen...
		print "<p><b> CRITICAL %s: False data in fax ID - check the module/source code! </b></p>" % webmin.text.get('error','').upper()
		raise capifaxwm.CSConfigError
	if not filetype or filetype!="sff" or not filetype!="cff":
		# this should never happen...
		print "<p><b> %s: False/unsupported filetype for jobdata file</b></p>" % webmin.text.get('error','').upper()
		raise capifaxwm.CSConfigError
	
	sendq=os.path.join(capifaxwm.UsersFax_Path,user,"sendq")+os.sep
	if (not os.access(sendq,os.W_OK)):
			print "<p>can't write to queue dir</p>"
			raise capifaxwm.CSConfigError # might be better to use s.th. else ...
	
	jobfile = sendq+"fax-"+jobid+".txt"
	try:
		lockfile=open(jobfile[:-3]+"lock","w")
		# lock so that it isn't deleted while sending
		fcntl.lockf(lockfile,fcntl.LOCK_EX | fcntl.LOCK_NB)
		cs_helpers.writeDescription(jobfile[:-3]+filetype,"dialstring=\""+dialstring+"\"\n"
			+"starttime=\""+timec+"\"\ntries=\""+tries+"\"\n"
			+"user=\""+user+"\"\naddressee=\""+addressee+"\"\nsubject=\""
			+subject+"\"\n")
		fcntl.lockf(lockfile,fcntl.LOCK_UN)
		os.unlink(jobfile[:-3]+"lock")
	except IOError,err:
		if (err.errno in (errno.EACCES,errno.EAGAIN)):
			print "<p><b>Job is currently in transmission. Can't abort.</b></p>"
	print '<p><b> Fax to %s %s (with ID %s) changed</b></p>' % (addressee,dialstring,jobid)

except capifaxwm.CSConfigError:
	print "<p><b>%s: False settings/config - please start from the main module page<br> and try not to call this page directly</b></p>" % webmin.text.get('error','').upper()
print "<hr>"
webmin.footer([("", "module index")])
