#!/usr/bin/python
# Written by Carsten <cibi@users.berlios.de>
# Copyright (C) 2003,2004 Carsten (http://capimin.berlios.de)
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License. 
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# Coding style: Max linewidth 120 chars
# - in change, not all lines fit currently 120
# 



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

capifaxwm.SwitchAndLoadConifg()

capifaxwm.capiconfig_init()

# soxvolume: default= 1.0, increases volume if >1.0 and decreace if <1.0
# added because of http://lists.berlios.de/pipermail/capisuite-users/2003-October/000363.html
# the next two declarations will be removed, as soons as the official webmin.py supports userconfig
# the default values will then be set by the wm_pytools.Extract[xy]Config calls
soxvolume="1"
intfaxformat=0
intcfaxformat=0
intvoiceformat=0

oggPermission = wm_pytools.ExtractIntConfig(webmin.config.get('ogg_download'),0,0,2)

if not capifaxwm._OldWebminpy and webmin.userconfig:
    soxvolume = str(wm_pytools.ExtractFloatConfig(webmin.userconfig.get('sox_volume'),soxvolume,0))
    intfaxformat = wm_pytools.ExtractIntConfig(webmin.userconfig.get('fax_download'),0,0,3)
    intcfaxformat = wm_pytools.ExtractIntConfig(webmin.userconfig.get('cfax_download'),0,0,2)
    intvoiceformat = wm_pytools.ExtractIntConfig(webmin.userconfig.get('voice_download'),0,0,2)

faxformat=['sff','tif','ps','pdf'][intfaxformat]
cfaxformat=['cff','ps','pdf'][intcfaxformat]
voiceformat=['wav','la','ogg'][intvoiceformat]

try:
    form = cgi.FieldStorage()
    if not form:
        raise capifaxwm.CSConfigError
    jobid = form.getfirst("jobid")    
    qtype = form.getfirst("qtype")
    colorfax = None
    
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
        if oggPermission==0 and voiceformat=="ogg":
            raise capifaxwm.CSConvError("Sorry, Ogg Vorbis download is not enabled")
        qpath=os.path.join(capifaxwm.UsersVoice_Path,webmin.remote_user,"received")+os.sep
        jobfile="voice-"+jobid+".txt"
        fileext=voiceformat
        if fileext=="wav":
            contenttype="audio/x-wav"
        elif fileext=="ogg":
            contenttype="application/ogg"
    else:
        raise capifaxwm.CSConfigError
    control=cs_helpers.readConfig(qpath+jobfile)

    if not control:
        raise capifaxwm.CSConfigError
    datafilename = control.get("GLOBAL","filename")    

    if not datafilename:
        raise capifaxwm.CSConfigError
    
    # color fax:
    # if os.path.splitext(datafilename)[1].lower()==".cff": # may be needed later
    if datafilename.endswith("cff"):
        fileext=cfaxformat
        colorfax=1
    basename=datafilename[:datafilename.rindex('.')+1]
    if fileext=="wav" or fileext=="ogg":
        rate=None
        if fileext=="ogg" and oggPermission==2:
            rate=32000
        capifaxwm.ConvertAudio2Sox(datafilename,basename+fileext,soxvolume,rate)
        datafilename = basename+fileext
    elif (not colorfax) and (fileext=="tif" or fileext=="ps" or fileext=="pdf"):
        capifaxwm.ConvertSFF(datafilename,basename+fileext,fileext)
        datafilename = basename+fileext
    elif colorfax and (fileext=="ps" or fileext=="pdf"):
        capifaxwm.ConvertCFF(datafilename,basename+fileext,fileext)
        datafilename = basename+fileext
    
        
    datafile = open(datafilename,'rb').read()
    sendname=jobfile[:-3]+fileext    
    sys.stdout.write('Content-type: '+contenttype+'; name="'+sendname+'"\r\n')    
    sys.stdout.write('Content-Disposition: attachment; filename="'+sendname+'"\r\n')    
    sys.stdout.write('Content-Length: '+str(len(datafile))+'\r\n')
    sys.stdout.write('\r\n')
    sys.stdout.write(datafile)
    if fileext=="wav" or fileext=="tif" or fileext=="ps" or fileext=="pdf" or fileext=="ogg":
        os.remove(datafilename)

except capifaxwm.CSConvError, e:
    webmin.header("Download", nomodule=1)    
    print "<hr>"
    print "<p><b> Convert-%s: %s </b></p>" % (webmin.text.get('error'),cgi.escape(e.message,1))
    print "<hr>"
    webmin.footer([("", "module index")])   

except:
    webmin.header("Download", nomodule=1)    
    print "<hr>"
    print "<p><b> %s: Request could not be parsed or file access error </b></p>" % webmin.text.get('error','').upper()
    print "<hr>"
    webmin.footer([("", "module index")])
