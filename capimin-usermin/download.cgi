#!/usr/bin/python
# download (transfer a file from the server to the client/user)
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
# http://capimin.berlios.de email: cibi@users.berlios.de


import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
import os, re, cgi
import webmin,cs_helpers,capifaxwm

qtype=""
jobid=""
qpath=""
contenttype="application/octet-stream"
fileext=""

capifaxwm.capiconfig_init()
webmin.init_config()


try:
    form = cgi.FieldStorage()
    if not form:
	raise capifaxwm.CSConfigError
    jobid = form.getfirst("jobid")    
    qtype = form.getfirst("qtype")
    
    if (not jobid) or (not qtype):
	raise capifaxwm.CSConfigError
    if capifaxwm.CheckJobID(jobid)==-1:
	raise capifaxwm.CSConfigError
    isVoice=0
    if qtype.find("voice")!=-1:
	isVoice=1

    if capifaxwm.checkconfig(isVoice)==-1:
	raise capifaxwm.CSConfigError

    if qtype=="faxreceived":
	qpath=os.path.join(capifaxwm.UsersFax_Path,webmin.remote_user,"received")+os.sep
	jobfile="fax-"+jobid+".txt"
	fileext="sff"
    elif qtype=="voicereceived":
	qpath=os.path.join(capifaxwm.UsersVoice_Path,webmin.remote_user,"received")+os.sep
	jobfile="voice-"+jobid+".txt"
	fileext="wav"
	contenttype="audio/x-wav"
    else:
	raise capifaxwm.CSConfigError
    control=cs_helpers.readConfig(qpath+jobfile)

    if not control:
	raise capifaxwm.CSConfigError
    datafilename = control.get("GLOBAL","filename")
    if not datafilename:
        raise capifaxwm.CSConfigError
    basename=datafilename[:datafilename.rindex('.')+1]
    if fileext=="wav":
	#la -> wav
	# don't use stdout as sox needs a file to be able to seek in it otherwise the header will be incomplete
	ret = os.spawnlp(os.P_WAIT,"sox","sox",datafilename,basename+"wav")
	
	if (ret or not os.access(basename+"wav",os.R_OK)):
    	    raise "conv-error","Error while calling sox. (ISDN voice->wav) Not installed?"
	datafilename = basename+"wav"
    
    datafile = open(datafilename,'rb').read()
    sendname=jobfile[:-3]+fileext    
    sys.stdout.write('Content-type: '+contenttype+'; name="'+sendname+'"\r\n')    
    sys.stdout.write('Content-Disposition: attachment; filename="'+sendname+'"\r\n')    
    sys.stdout.write('Content-Length: '+str(len(datafile))+'\r\n')
    sys.stdout.write('\r\n')
    sys.stdout.write(datafile)
    if fileext=="wav":
	os.unlink(datafilename)
except "conv-error",errormessage:
    webmin.header("Download", config=1, nomodule=1)
    print "<hr>"
    print "<p><b> Convert-Error:",errormessage,"</b></p>"
    print "<hr>"
    webmin.footer([("", "module index")])   

except:
    webmin.header("Download", config=1, nomodule=1)
    print "<hr>"
    print "<p><b> ERROR: Request could not be parsed or file access error </b></p>"
    print "<hr>"
    webmin.footer([("", "module index")])

