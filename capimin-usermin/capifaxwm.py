# Most/all fax functions in this file are  form (modified for html/webmin):
#             capisuitefax - capisuite tool for enqueuing faxes
#            ---------------------------------------------------
#    copyright            : (C) 2002 by Gernot Hillier
#    email                : gernot@hillier.de
#    version              : $Revision: 1.2 $
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.


import webmin
import os, sys, re, getopt, commands, fcntl,errno,time,string,shutil,pwd
import cs_helpers

webmin.init_config()
# user independent path:
UsersFax_Path=""
UsersVoice_Path=""

tempdir="/tmp"

CAPI_config=None


def capiconfig_init(file=""):
    global CAPI_config,UsersFax_Path,UsersVoice_Path
    CAPI_config=cs_helpers.readConfig(file)
    if not CAPI_config:
	UsersFax_Path=""
	UsersVoice_Path=""
	return -1
    UsersFax_Path=cs_helpers.getOption(CAPI_config,"","fax_user_dir")
    if UsersFax_Path=="":
	return -1
    # optional value:
    UsersVoice_Path=cs_helpers.getOption(CAPI_config,"","voice_user_dir")

# checks the values set by capiconfig_init(file="")
# unlike capiconfig_init it doesn't load any extern (e.g. config file) values 
# and doesn't reset them if any of the config settings is false
def checkconfig(checkvoice=0):
    global CAPI_config,UsersFax_Path,UsersVoice_Path
    if not CAPI_config or not UsersFax_Path:
       return -1
    if (checkvoice==1 or checkvoice=="voice") and not UsersVoice_Path:
	return -1
    
# check if the user is a valid capisuitefax user
# set verbose=1 if you want a (html formated) error messages to be printed out
# return value: 0 = false , 1 = true 
def checkfaxuser(user,verbose=0):
    if (not CAPI_config.has_section(user)):
	if verbose==1:
	    print "<p><b> ERROR: user \""+user+"\" is not a valid capifaxuser</b></p>"
	return 0
    else:
	return 1


def showfaxlist(user,changepage="change.cgi",abortpage="abort.cgi"):
    if (checkconfig() == -1) or (checkfaxuser(user,1) == 0):
        raise CSConfigError

    sendq=UsersFax_Path    
    sendq=os.path.join(sendq,user,"sendq")+"/"
    #print '<p><b> %s: %s</b></p>' % (webmin.text['csfax_user'],user)
    print '<table border="1">\n <tr bgcolor=#%s>' % webmin.tb
    print '   <th>%s</th><th>%s</th><th>%s</th><th>%s</th>' %  (webmin.text['index_id'],webmin.text['index_dialstring'],webmin.text['index_addressee'],webmin.text['index_tries'])
    print '   <th>%s</th><th>%s</th><th><b>&nbsp;</b></th><th>%s</th>\n </tr>' % (webmin.text['index_nexttry'],webmin.text['index_subject'],webmin.text['index_toabort'])
    
    files=os.listdir(sendq)
    files=filter (lambda s: re.match("fax-.*\.txt",s),files)

    for job in files:
	control=cs_helpers.readConfig(sendq+job)
	faxid = re.match("fax-([0-9]+)\.txt",job).group(1)
	starttime=(time.strptime(control.get("GLOBAL","starttime")))[0:8]+(-1,)

	print ' <tr bgcolor=#%s>\n  <form METHOD="POST" ACTION="%s">' % (webmin.cb,changepage)	
        print "   <td>&nbsp;%s</td>" % faxid
	print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","dialstring")
	print '   <td><input TYPE="TEXT" NAME="formDialAddressee" SIZE="15" MAXLENGTH="40" value="%s"></td>' % cs_helpers.getOption(control,"GLOBAL","addressee","")
	print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","tries")
	
	print '   <td nowrap><input name="year" type="text" size="4" maxlength="4" value="%s">-<select name="month">' % starttime[0]
	for i in range(1,13):
	    selected =""
    	    if i==starttime[1]:
		selected=' selected="selected"'
	    print '        <option value="%s"%s>%s</option>' % (i,selected,webmin.text["smonth_"+str(i)])
	print '      </select>-<input name="day" size="2" maxlength="2" value="%s">' % starttime[2]
	print '        &nbsp;&nbsp;<input name="hour" size="2" maxlength="2" value="%s">:<input name="min" size="2" maxlength="2" value="%02d"></td>' % (starttime[3],starttime[4])
	#print '   <td><input TYPE="TEXT" NAME="datetime" SIZE="8" MAXLENGTH="12" value="'+time1+'">'
	#print '       <input TYPE="TEXT" NAME="date" SIZE="10" MAXLENGTH="16" value="'+time2+'"></td>'
	
	print '   <td><input TYPE="TEXT" NAME="formSubject" SIZE="30" MAXLENGTH="40" value="%s"></td>' % cs_helpers.getOption(control,"GLOBAL","subject","")
	print '   <input type="hidden" name="formFaxID" value="%s">' % faxid
	print '   <input type="hidden" name="formDialString" value="%s">' % control.get("GLOBAL","dialstring")
	print '   <input type="hidden" name="formTries" value="%s">' % control.get("GLOBAL","tries")
	print '   <input type="hidden" name="formOrgDate" value="%s">' % control.get("GLOBAL","starttime")
	print '   <td><input TYPE="SUBMIT" VALUE="%s"></td>\n  </form>' % webmin.text['index_change']
	print '   <td>&nbsp;&nbsp;<i><a href="%s?jobid=%s">%s</a></i></td>' % (abortpage,faxid,webmin.text['index_toabort'])
#	print '  <form ACTION="%s"><input type="hidden" name="jobid" value="%s">' % (abortpage,faxid)
#	print '   <td><input TYPE="SUBMIT" VALUE="%s"></td>\n  </form>' % webmin.text['index_toabort']
	print ' </tr>'


    print "</table>"

# List received list for fax and voice calls
# fileprefix can be "fax" or "voice". this is also used to get the right dir path
def showreceivedlist(user,fileprefix="fax",forwardopt=0,newpage="newfax.cgi",dldpage="",removepage=""):
    if (checkconfig(fileprefix) == -1) or (checkfaxuser(user,1) == 0):
        raise CSConfigError
    
    path=""
    qtype=""
    if fileprefix =="fax":
	path = UsersFax_Path	
	qtype = "faxreceived"
    elif fileprefix == "voice":
	path = UsersVoice_Path
	qtype = "voicereceived"
    else:
	raise CSConfigError
        
    path=os.path.join(path,user,"received")+"/"
    print '<table border="1">\n <tr bgcolor=#%s>' % webmin.tb
    print '   <th>%s</th><th>From</th><th>To (MSN)</th><th>Time</th><th>ISDN cause</th><th>File</th>' %  (webmin.text['index_id'])
    if forwardopt==1:
	print '   <th>&nbsp;</td>'
    if removepage:
	print '   <th>&nbsp;</td>'
    print ' </tr>'
    
    files=os.listdir(path)
    files=filter (lambda s: re.match(fileprefix+"-.*\.txt",s),files)

    for job in files:
	print ' <tr bgcolor=#%s>' % webmin.cb
	control=cs_helpers.readConfig(path+job)
	jobid = re.match(fileprefix+"-([0-9]+)\.txt",job).group(1)
        print "  <td>&nbsp;%s</td>" % jobid
	print "  <td>&nbsp;%s</td>" % control.get("GLOBAL","call_from")
	print "  <td>&nbsp;%s</td>" % control.get("GLOBAL","call_to")
	print "  <td nowrap>&nbsp;%s</td>" % control.get("GLOBAL","time")
	print "  <td>&nbsp;%s</td>" % control.get("GLOBAL","cause")

	if forwardopt==1:
	    print '  <form METHOD="POST" ACTION="%s"><input type="hidden" name="formfaxid" value="%s"><input type="hidden" name="qtype" value="faxreceived">\
<input type="hidden" name="faxcreate" value="forward"><td><input TYPE="SUBMIT" VALUE="%s"></td></form>' % (newpage,jobid,webmin.text['index_forward'])

	if dldpage:
#	    print '  <form METHOD="POST" ACTION="%s"><input type="hidden" name="jobid" value="%s">' % (dldpage,jobid)
#	    print '   <input type="hidden" name="qtype" value="%s"><td><input TYPE="SUBMIT" VALUE="%s"></td></form>' % (qtype,webmin.text['index_download'])
	    print '   <td><b><a href="%s?jobid=%s&qtype=%s">%s</a></b></td>' % (dldpage,jobid,qtype,webmin.text['index_download'])
	else:
	    print "  <td>&nbsp;%s</td>" % control.get("GLOBAL","filename") # TODO?:change it to file name only

	if removepage:
#	    print '   <form ACTION="%s"><input type="hidden" name="jobid" value="%s"><input type="hidden" name="qtype" value="%s">' % (removepage,jobid,qtype)
#	    print '    <td><input TYPE="SUBMIT" VALUE="%s"></td></form>' % webmin.text['delete']
	    print '   <td>&nbsp;&nbsp;<i><a href="%s?jobid=%s&qtype=%s">%s</a></i></td>' % (removepage,jobid,qtype,webmin.text['delete'])
	print "</tr>"
    print "</table>"

#will be replaced by a common delete job function
def removejob(user,jobid,qtype):
    if (checkconfig() == -1) or (checkfaxuser(user,1) == 0):
        raise CSConfigError
    if qtype=="faxsend":
        qpath = UsersFax_Path
	queue = "sendq"
	prefix="fax"
    elif qtype=="faxreceived":
	qpath = UsersFax_Path
	queue = "received"
	prefix="fax"
    elif qtype=="voicereceived":
	qpath = UsersVoice_Path
	queue = "received"
	prefix="voice"
    else:
	return -1
    
    qpath=os.path.join(qpath,user,queue)+os.sep

    if  jobid=="":
	print "<p><b> ERROR: Invalid Fax ID \""+jobid+"\" or false capisuitefax queue path: \""+qpath+"\"</b></p>"
	return -1

    job=prefix+"-"+jobid+".txt"

    if (not os.access(qpath+job,os.W_OK)):
	print "<p><b> Fax ("+jobid+") is not valid job to remove</b></p>",job
	return -1
    control=cs_helpers.readConfig(qpath+job)
    datafile=control.get("GLOBAL","filename")
    if not datafile:
        return -1
    try:    
	lockfile=open(qpath+job[:-3]+"lock","w")
	# lock so that it isn't deleted while sending
	fcntl.lockf(lockfile,fcntl.LOCK_EX | fcntl.LOCK_NB)
	os.unlink(qpath+job)
	os.unlink(datafile)
	fcntl.lockf(lockfile,fcntl.LOCK_UN)
	os.unlink(qpath+job[:-3]+"lock")
    except IOError,err:
	if (err.errno in (errno.EACCES,errno.EAGAIN)):
	    print "<p><b>Job is currently in transmission or in similar use. Can't remove.</b></p>"


# check a dialstring, allows typical "help chars"/separators
def CheckDialString(dialstring):
    if not dialstring: 	return -1
    if re.compile("[^0-9+()/\- ]+").search(dialstring):
	return -1

# Converts a dialstring, only allows numbers and "+"
# It performs first a check with "CheckDialString(dialstring)"
def ConvertDialString(dialstring):
    if CheckDialString(dialstring)==-1:
	return None
    
    # delete common dial separators 
    dialstring=dialstring.translate(string.maketrans("",""),"-/ ()")
    if not dialstring: return None # this should never happen... (done in CheckDialString)
    return dialstring

def CheckJobID(jobid):
    if not jobid:
	return -1
    if re.compile("[^0-9]").search(jobid):
	return -1

def sendfax(user,dialstring,sourcefile,cstarttime="",addressee="",subject="",useprefix=None):
    if (checkconfig == -1) or (checkfaxuser(user,1) == 0) or (not sourcefile):
	raise CSConfigError
    if not dialstring:
	print "<p> empty dialstring </p>"
        return -1 # -TODO-Error handling
	
    if ((cs_helpers.getOption(CAPI_config,user,"outgoing_MSN","")=="") and (CAPI_config.get(user,"fax_numbers","")=="")):
	print "<p><b> Sorry, your are not allowed to send a fax</b></p>"
	return -1
    
    # Convert to empty string, if set to "None"
    if addressee==None: addressee=""
    if subject==None: subject=""
    
    # filter out common separators from dialstring, check it
    dialstring=dialstring.translate(string.maketrans("",""),"-/ ()")
    if re.compile("[^0-9\+]+").search(dialstring):
	print "<p> Invalid dialstring </p>"
	return -1
    prefix=cs_helpers.getOption(CAPI_config,user,"dial_prefix","")
    if (useprefix):
            dialstring=prefix+dialstring
    
    if (not os.access(sourcefile,os.R_OK)):
	print "<p><b>ERROR: cannot read fax source file:%</b></p>" % faxfile
	return -1
    sendq = os.path.join(UsersFax_Path,user,"sendq")+"/"
    newname=cs_helpers.uniqueName(sendq,"fax","sff")
    
    # --TODO--Error check!!!!
    shutil.copy(sourcefile,newname)
    
    if not cstarttime:
	cstarttime = time.ctime()
    
    cs_helpers.writeDescription(newname,"dialstring=\""+dialstring+"\"\n"
      +"starttime=\""+cstarttime+"\"\ntries=\"0\"\n"
      +"user=\""+user+"\"\naddressee=\""+addressee+"\"\nsubject=\""
      +subject+"\"\n")
    
    os.chmod(newname,0600)
    os.chmod(newname[:-3]+"txt",0600)
    if (os.getuid()==0):
	user_entry=pwd.getpwnam(user)
	os.chown(newname,user_entry[2],user_entry[3])
	os.chown(newname[:-3]+"txt",user_entry[2],user_entry[3])

    print "<p>",sourcefile,"successful enqueued as",newname,"for",dialstring,"</p>"
    
        

    

#def abortfax(user, faxid):
#    if user == "" or faxid == "":
#	print "<p><b>Invalid user: "+user+" or Fax ID path: "+faxid+"</b></p>"
#	return -1
#    print "<p><b> Trying to abort Fax for user: "+faxid+",<br/>"
#    print " the fax id is: "+faxid+"<br>"
#    print " capisuitefax output:</b>"
#    (stat, cmdoutput) = commands.getstatusoutput('capisuitefax -u '+user+' -a '+faxid)    
#    print "<p><pre>"+cmdoutput+"</pre><br>"
#    print "Return Code: %d </p>" % (stat)

class CSConfigError(Exception):
    pass
class FormInputError(Exception):
    pass
