# Most/all fax functions in this file are  form (modified for html/webmin):
#             capisuitefax - capisuite tool for enqueuing faxes
#            ---------------------------------------------------
#    copyright            : (C) 2002 by Gernot Hillier
#    email                : gernot@hillier.de
#    version              : $Revision: 1.13 $
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
#for load_user_config()
import pwd

webmin.init_config()
# check if python modul HTMLGen is installed, and if not
# disable the theme use by Web/Usermin. This is done by an
# "unoffical" way: the path to the theme file is deleted from
# the webmin.tconfig dictionary
try:
    import HTMLgen
except:
    if webmin.tconfig.has_key('functions'):
	webmin.tconfig['functions'] = "-"

# -----------------
# needed, because the current webmin.py does not contain create_user_config_dirs and userconfig
_OldWebminpy=None
_showconfig=1

def SwitchAndLoadConifg():
    try:	
        webmin.switch_to_remote_user()
	webmin.create_user_config_dirs()
	_showconfig=1
    except NotImplementedError:
	_OldWebminpy=1
        _showconfig=None
# -----------------



       
# setup:
# path to the sox (audio converter) program
sox="sox"


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



def load_user_config():
    """ This function is simialar as webmin's api create_user_config_dirs() function,
    but it only reads the config and doesn't create any directories.
    One reason for this, because without a call to switch_user, the webmin api
    function would create the dir as root, which would then be not writeable by
    the default Usermin user config page. (it would be possible to create the dirs
    as the remote user in this function too, but that's currently not required by this module)
    """

    if not webmin.gconfig.has_key('userconfig'): return
    if not webmin.remote_user_info:
	uinfo = pwd.getpwnam(webmin.remote_user)	
    else:
	uinfo = webmin.remote_user_info
    
    if not uinfo or not uinfo[5]: return
    
    webmin.user_config_directory = os.path.join(uinfo[5],webmin.gconfig['userconfig'])
    _skip_user_config_file = None
    if not os.path.exists(webmin.user_config_directory):
	# os.mkdir(user_config_directory,0755)
	_skip_user_config_file = 1
	webmin.user_config_directory=None
    if webmin.module_name:
	webmin.user_module_config_directory = os.path.join(webmin.user_config_directory,webmin.module_name)	
	if not _skip_user_config_file and not os.path.exists(webmin.user_module_config_directory):
	    # os.mkdir(user_module_config_directory,0755)
	    skip_user_config_file = 1
	    webmin.user_module_config_directory=None
	webmin.userconfig={}	
	webmin.read_file_cached(webmin.module_root_directory+os.sep+'defaultuconfig',webmin.userconfig)
	webmin.read_file_cached(webmin.module_config_directory+os.sep+'uconfig',webmin.userconfig)
	if not _skip_user_config_file:
	    webmin.read_file_cached(webmin.user_module_config_directory+os.sep+'config',webmin.userconfig)




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
	raise CSConfigError
    UsersFax_Path=cs_helpers.getOption(CAPI_config,"","fax_user_dir",default="")
    if not UsersFax_Path:
	raise CSConfigError
    GlobalSpool_Path=cs_helpers.getOption(CAPI_config,"","spool_dir",default="")
    if not GlobalSpool_Path:
	raise CSConfigError
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

def removejob(user,jobid,cslist):
    if (checkconfig() == -1) or (checkfaxuser(user,1) == 0):
        raise CSConfigError
    if not listtypes.has_key(cslist) or CheckJobID(jobid)==-1:
	raise CSConfigError
    
    qpath=BuildListPath(cslist,user)
    
    job =""
    if listtypes[cslist][1]==1:
	job=user+"-"
    job=job+listtypes[cslist][0]+"-"+jobid+".txt"
    #job=prefix+"-"+jobid+".txt"

    if (not os.access(qpath+job,os.W_OK)):
	raise CSRemoveError('Job file "%s" (ID:%s List:%s) is not valid job to remove' % (job,jobid,cslist))	
	
    control=cs_helpers.readConfig(qpath+job)
    
    # in capisuite 0.4.3, the filename options in failed and done store the original file path
    # (e.g. /var/spool/capisuite/users/me/senq/fax-12.sff).
    datafile=control.get("GLOBAL","filename")
    if cslist=="faxdone" or cslist=="faxfailed":
	# color fax check:
	fileext="sff"
        #if os.path.splitext(datafile)[1].lower()==".cff":
	if datafile.endswith("cff"):
	    fileext="cff"
	datafile=qpath+job[:-3]+fileext
    if not datafile:
	raise CSRemoveError('Job file "%s" (ID:%s List:%s) does not contain a link to a datafile (e.g. sff faxfile) => Invalid job file' % (job,jobid,cslist))
    try:    
	lockfile=open(qpath+job[:-3]+"lock","w")
	# lock so that it isn't deleted while sending (or else)
	fcntl.lockf(lockfile,fcntl.LOCK_EX | fcntl.LOCK_NB)
	os.unlink(qpath+job)
	os.unlink(datafile)
	fcntl.lockf(lockfile,fcntl.LOCK_UN)
	os.unlink(qpath+job[:-3]+"lock")
    except IOError,err:
	if (err.errno in (errno.EACCES,errno.EAGAIN)):
	    raise CSRemoveError("Job is currently in transmission or in similar use. Can't remove.")


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
    
    filetype = os.path.splitext(sourcefile)[1].lower()[1:] # splittext always returns a list of 2, so no "None" check needed
    if not filetype:
	print "<p><b> Invalid input (fax) file </b></p>"
	raise CSConfigError
    
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
    newname=cs_helpers.uniqueName(sendq,"fax",filetype)
    
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
    


def ConvertAudio2Sox(lafile,wavfile,volume=1.0):
    if not lafile or not wavfile:
        raise CSConvError("False parameter (no in and/or outputfile)")
	    
    #la -> wav
    # don't use stdout as sox needs a file to be able to seek in it otherwise the header will be incomplete
    ret = os.spawnlp(os.P_WAIT,"sox","sox","-v",volume,lafile,wavfile)
	
    if (ret or not os.access(wavfile,os.R_OK)):
	raise CSConvError("Error while calling sox. File damaged or sox not installed?")


def ConvertSFF(sfffile,destfile,desttype="pdf"):
    if not sfffile or not destfile or not desttype:
	raise CSConvError("False parameter (no in and/or outputfile)")
    if desttype!="pdf" and desttype!="ps" and desttype!="tif":
	raise CSConvError("False parameter (no in and/or outputfile)")
    
    # sff -> tif
    if desttype=="tif":
	outfile=destfile
    else:
	outfile=destfile+".tif"
    ret=os.spawnlp(os.P_WAIT,"sfftobmp","sfftobmp","-tif",sfffile,outfile)
    if (ret or not os.access(outfile,os.F_OK)):
	CSConvError("Can't convert sff to tif. sfftobmp not installed?")
    if desttype=="tif":
	return
    
    # tif -> ps
    infile=outfile
    if desttype=="ps":
	outfile=destfile
    else:
	outfile=destfile+".ps"
    ret=os.spawnlp(os.P_WAIT,"tiff2ps","tiff2ps","-a",infile,"-O",outfile)
    if (ret or not os.access(outfile,os.F_OK)):
	raise CSConvError("Can't convert tif to ps (tif file is created from sff). tiff2ps not installed?")
    remtempfailed=[]
    try:
        os.remove(infile)
    except:
	remtempfailed.append(infile)
    if desttype=="ps":
	return remtempfailed
    
    # ps -> pdf
    infile=outfile
    ret=os.spawnlp(os.P_WAIT,"ps2pdf","ps2pdf",infile,destfile)
    if (ret or not os.access(destfile,os.F_OK)):
	raise CSConvError("Can't convert ps to pdf (ps created from sff -> tif -> ps ). ps2pdf not installed?")
    try:
        os.remove(infile)
    except:
	remtempfailed.append(infile)
    return remtempfailed
 
def ConvertCFF2PDF(cfffile,pdffile):
    raise NotImplementedError
    if not cfffile or not pdffile:
	raise CSConvError("False parameter (no in and/or outputfile)")

def ConvertPS2SFF(psfile,sfffile):
    if not psfile or not sfffile:
	raise CSConvError("False parameter (no in and/or outputfile)")
    
    psfilename = os.path.basename(psfile)
    if not psfilename:
	raise CSConvError("False parameter (no in and/or outputfile)")
    if psfile.startswith("@") or psfilename.startswith("@"):
	raise CSConvError('Illegal char found in ps file for use with "gs"')
    #ret = os.spawnlp(os.P_WAIT,"gs","gs","-dNOPAUSE","-dQUIET","-dBATCH","-sDEVICE=cfax","-sOutputFile="+cs_helpers.escape(sfffile),cs_helpers.escape(psfile))
    #ret = os.spawnlp(os.P_WAIT,"gs","-dNOPAUSE -dQUIET -dBATCH -sDEVICE=cfax -sOutputFile="+cs_helpers.escape(sfffile)+" "+cs_helpers.escape(psfile))
    gscmd = "gs -dNOPAUSE -dQUIET -dBATCH -sDEVICE=cfax -sOutputFile="+cs_helpers.escape(sfffile)+" "+cs_helpers.escape(psfile)
    (ret,out) = commands.getstatusoutput(gscmd)
    
    if (ret or not os.access(sfffile,os.R_OK)):
	raise CSConvError("Failed  converting ps->sff. PS-file damaged/false format or gs not installed?")
    


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
# added because Python (2.2.1) or at least my code, doesn't catch the string exception type ("conv-error","messgae")
# when the exception is handled in another module
class CSConvError(Exception):
    def __init__(self, message):
	self.message = message
    def __str__(self):
	return repr(self.message)

class CSRemoveError(Exception):
    """ errortype:: to define the type of the error:
		   0=default/undefined,1=false job,2=access error,3=job in use
    """
    def __init__(self, message,errortype=0):
	self.message = message
	self.errortype = errortype
    def __str__(self):
	return repr(self.message)
    def ErrorType():
	return self.errortype

