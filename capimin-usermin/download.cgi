#!/usr/bin/python
# download (transfer a file from the server to the client/user)
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
# http://capimin.berlios.de email: cibi@users.berlios.de

# File conversation taken from:
#         cs_helpers.py - some helper functions for CapiSuite scripts
#         -----------------------------------------------------------
#    copyright            : (C) 2002 by Gernot Hillier
#    email                : gernot@hillier.de
#    version              : $Revision: 1.7 $
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.


import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
import os, re, cgi
import webmin,cs_helpers,capifaxwm,wm_pytools

qtype=""
jobid=""
qpath=""
contenttype="application/octet-stream"
fileext=""

#webmin.init_config()
# -----------------
# needed, because the current webmin.py does not contain create_user_config_dirs and userconfig
OldWebminpy=None
try:
    webmin.switch_to_remote_user()
    webmin.create_user_config_dirs()
except NotImplementedError:
    OldWebminpy=1
# -----------------

capifaxwm.capiconfig_init()

# soxvolume: default= 1.0, increases volume if >1.0 and decreace if <1.0
# added because of http://lists.berlios.de/pipermail/capisuite-users/2003-October/000363.html
soxvolume="1"
intfaxformat=0
if not OldWebminpy and webmin.userconfig:
    if webmin.userconfig.has_key('sox_volume'):
	soxvolume = str(wm_pytools.ExtractFloatConfig(webmin.userconfig['sox_volume'],soxvolume,0))
    if webmin.userconfig.has_key('fax_download'):
	intfaxformat = wm_pytools.ExtractIntConfig(webmin.userconfig['fax_download'],0,0,3)

faxformat=['sff','tif','ps','pdf'][intfaxformat]

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
	fileext=faxformat
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
    # color fax:
    if os.path.splitext(datafilename)[1].lower()==".cff":
	fileext="cff"
    basename=datafilename[:datafilename.rindex('.')+1]
    if fileext=="wav":
	capifaxwm.ConvertAudio2Sox(datafilename,basename+fileext,soxvolume)
	datafilename = basename+fileext
    if fileext=="tif" or fileext=="ps" or fileext=="pdf":	
	capifaxwm.ConvertSFF(datafilename,basename+fileext,fileext)
	datafilename = basename+fileext
	    
    datafile = open(datafilename,'rb').read()
    sendname=jobfile[:-3]+fileext    
    sys.stdout.write('Content-type: '+contenttype+'; name="'+sendname+'"\r\n')    
    sys.stdout.write('Content-Disposition: attachment; filename="'+sendname+'"\r\n')    
    sys.stdout.write('Content-Length: '+str(len(datafile))+'\r\n')
    sys.stdout.write('\r\n')
    sys.stdout.write(datafile)
    if fileext=="wav" or fileext=="tif" or fileext=="ps" or fileext=="pdf":
	os.remove(datafilename)
except "conv-error",errormessage:
    webmin.header("Download", nomodule=1)    
    print "<hr>"
    print "<p><b> Convert-Error:",errormessage,"</b></p>"
    print "<hr>"
    webmin.footer([("", "module index")])   

except:
    webmin.header("Download", nomodule=1)    
    print "<hr>"
    print "<p><b> ERROR: Request could not be parsed or file access error </b></p>"
    print "<hr>"
    webmin.footer([("", "module index")])
