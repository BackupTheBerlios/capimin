# Mo>Jst/all fax functions in this file are  form (modified for html/webmin):
#             capisuitefax - capisuite tool for enqueuing faxes
#            ---------------------------------------------------
#    copyright            : (C) 2002 by Gernot Hillier
#    email                : gernot@hillier.de
#    version              : $Revision: 1.3 $
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
# for the rest: http://capimin.berlios.de email: cibi@users.berlios.de


import webmin
import os, sys, re, getopt, commands, fcntl,errno,time,string,shutil,pwd
import cs_helpers

webmin.init_config()
# user independent path:
UsersFax_Path=""
UsersVoice_Path=""

listpath = None
CAPI_config=None
#faxsend = [0,'fax', 0,'fax_user_dir','sendq']
#faxreceived = [0,'fax', 0,'fax_user_dir','received']
#faxfailed = [0,'fax', 1,'spool_dir','failed']
#faxdone = [0,'fax', 1,'spool_dir','done']
#voicereceived = [1,'voice',0,'voice_user_dir','received']



# [fileprefix,userprefix,pathtype,dirname]
# fileprefix: "fax" or "voice"
# userprefix: 0=no,files in userspecific dir , 1=yes (e.g. "fax-0.sff","user-fax-0.sff")
# pathtype: key for "listpath" dictionary
listtypes = {'faxsend':('fax', 0,'fax_user_dir','sendq'),
	'faxreceived':('fax', 0,'fax_user_dir','received'),
	'faxfailed':('fax', 1,'spool_dir','failed'),
	'faxdone':('fax', 1,'spool_dir','done'),
	'voicereceived':('voice',0,'voice_user_dir','received')}

# @brief Generates the path for a list/queue, capiconfig_init(...) pre-required
#
# As it makes only sence to call this function, after everything is checked, i skipped
# the config check here.
# if listtypes[cslisttype][1], the userprefix, is set to 0, an additional user dir
# will be added, but only when the user param is set  (e.g. path/userdir/listdir)
#
# @cslisttype must be a key from dict "listtype"
# @user default is an empty string
#
# @return Generated path is returned, otherwise an exception is raised
def BuildListPath(cslisttype,user=""):
    
    def checkinfo(listinfo):
	if type(listinfo) is not tuple: return None
	if len(listinfo)!=4: return None
	if type(listinfo[0]) is not str: return None
	if type(listinfo[1]) is not int: return None
	if type(listinfo[2]) is not str: return None
	if type(listinfo[3]) is not str: return None
	return 1
	
    if not listtypes.has_key(cslisttype) or not checkinfo(listtypes[cslisttype]):
	raise "CSPath","BuildListPath: invalid listtype"

    path=listpath[listtypes[cslisttype][2]]
    if listtypes[cslisttype][1]==0 and user!="":
	path=os.path.join(path,user,listtypes[cslisttype] [3] )+os.sep
    else:
        path=os.path.join(path,listtypes[cslisttype] [3] )+os.sep
    return path

def capiconfig_init(file=""):
    global CAPI_config,UsersFax_Path,UsersVoice_Path,listpath
    UsersFax_Path=""
    UsersVoice_Path=""
    GlobalSpool_Path=""
    listpath = None

    CAPI_config=cs_helpers.readConfig(file)
    if not CAPI_config:
	return -1
    UsersFax_Path=cs_helpers.getOption(CAPI_config,"","fax_user_dir",default="")
    if UsersFax_Path=="":
	return -1
    GlobalSpool_Path=cs_helpers.getOption(CAPI_config,"","spool_dir",default="")
    if GlobalSpool_Path=="":
	return -1
    # optional value:
    UsersVoice_Path=cs_helpers.getOption(CAPI_config,"","voice_user_dir",default="")
    listpath = {"fax_user_dir":UsersFax_Path,"spool_dir":GlobalSpool_Path,"voice_user_dir":UsersVoice_Path}

# @brief checks the values set by capiconfig_init(...)
#
# unlike capiconfig_init it doesn't load any extern (e.g. config file) values
# and doesn't reset them if any of the config settings is false
#
# @checkvoice can be 1 or "voice" if the config should be checked for the corret voice settings
#
# @return -1 if check failed (false config/settings), other cases not defined
def checkconfig(checkvoice=0):    
    try:
	if not CAPI_config or not UsersFax_Path or not listpath:
	    return -1
        
	if (checkvoice==1 or checkvoice=="voice") and not UsersVoice_Path:
	    return -1
        
    
        # theoretical, listpath should always have at least an empty key here,
        # but to be sure: (especially, because other function might assume the existents)
	if not listpath.has_key('fax_user_dir') or not listpath.has_key('spool_dir'):
	    return -1
	if listpath['fax_user_dir']=="" or listpath['spool_dir']=="":
	    return -1
    
    
	if checkvoice==1 or checkvoice=="voice":
    	    # theoretical, listpath should always have at least an empty voice_user_dir here,
	    # but to be sure: (especially, because other function might assume the existents)
	    if not listpath.has_key('voice_user_dir'):
		return -1
	    if listpath['voice_user_dir']=="":
		return -1
    except:
	# handle every exception as an error in the configuration
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
