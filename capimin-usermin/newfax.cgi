#!/usr/bin/python
# forward a fax: import the data from a queue file and show a form to enter a new destination
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
import cs_helpers,os, re,getopt, cgi, time, fcntl, shutil, tempfile


subject = ""
addressee = ""
dialstring = ""
formActionType = ""
faxfile = ""

# for forwarding faxes:
fjobid=""
fqtype=""

# userswitch can currently not be used here see capisuite bug 50
# http://www.capisuite.de/capisuite/mantis/view_bug_page.php?f_id=0000050
# update: added "check and set" for this case, it works now
capifaxwm.SwitchAndLoadConifg()

capifaxwm.capiconfig_init()

webmin.header("Capisuitefax - create/forward/answer fax", config=None, nomodule=1)
print "<hr>"


# Converts global string values to empty strings, if they are not assigned (None)
# used for the form output
def NoneStringToEmpty():
    global subject,addressee,dialstring
    if subject==None: subject=""
    if addressee==None: addressee=""
    if dialstring==None: dialstring=""


def rmfile(file):
    """ remove a file, don't throw if it doesn't exists
    or fail to remove
    """
    if not file: return -1
    try:
	os.remove(file)
    except:
	return -1
    

# read a capisuitefax file (e.g. from the received dir)
# and copy the fax file to a tmp location (in case the file is deleted, before it is copied in the send queue)
# Security note: if you use python 2.3, change to tempfile.mkstemp
def importqfax(jobid,qtype):
    if (capifaxwm.CheckJobID(jobid)==-1) or not qtype:
	raise capifaxwm.CSConfigError
    qpath=""
    if qtype=="faxreceived":
	qpath=os.path.join(capifaxwm.UsersFax_Path,webmin.remote_user,"received")+os.sep
	jobfile="fax-"+jobid+".txt"    
    # nothing else currently supported
    else:
	raise capifaxwm.CSConfigError
	
    control=cs_helpers.readConfig(qpath+jobfile)
    if not control:
	print "<p><b> Failed to read fax info file: %s</b></p>" % qpath+jobfile	
	raise capifaxwm.CSConfigError
	
    jobbinfile = control.get("GLOBAL","filename")
    if jobbinfile==None: jobbinfile="" # to avoid exception with splittext, check done below with filetypedot
    filetypedot = os.path.splitext(jobbinfile)[1].lower() # splittext always returns a list of 2, so no "None" check needed     
    if not filetypedot:
	print "<p><b> Error in jobfile: no data/invalid filename found (jobid: %s )</b></p>" % jobid
	raise capifaxwm.CSConfigError

    # Security note: if you use python 2.3, change to tempfile.mkstemp
    # in python version earlier than 2.3, mktemp hasn't the option to specify a directory 
    tmpjobfile = os.path.basename(tempfile.mktemp(".tempfax"+filetypedot)) 
    newpath=os.path.join(capifaxwm.UsersFax_Path,webmin.remote_user,"sendq")+os.sep
    if not tmpjobfile or not newpath or not jobbinfile :	
	raise capifaxwm.CSConfigError
    
    shutil.copy(jobbinfile,newpath+tmpjobfile)
    
    # read optional values from the job txt file
#    dialstring = control.get("GLOBAL","dialstring")
#    subject = control.get("GLOBAL","subject")
#    addressee = control.get("GLOBAL","addressee")
    return newpath+tmpjobfile

def shownewform(fjobid="",fqtype=""):
    curtime = time.localtime()
    NoneStringToEmpty()
    enctype=""
    title="Forward"
    if formActionType.startswith("new"):
	enctype='enctype="multipart/form-data"'
	title="New"

    
    
    print '<table border="1">' 
    print ' <tr bgcolor=#%s><th>%s</th></tr>  ' % (webmin.tb,title)
    print ' <tr bgcolor=#%s><td><form METHOD="POST" ACTION="newfax.cgi" %s>' % (webmin.cb,enctype)
    print '   <table>'
    print '    <tr><td><b>%s</b></td><td>' % webmin.text['newfax_senddate']
    print '        <input name="year" type="text" size="4" maxlength="4" value="%s">-<select name="month">' % curtime[0]
    for i in range(1,13):
	selected =""
	if i==curtime[1]:
	    selected=' selected="selected"'
	print '        <option value="%s"%s>%s</option>' % (i,selected,webmin.text["smonth_"+str(i)])
    
    print '        </select>-<input name="day" size="2" maxlength="2" value="%s">' % curtime[2]
    print '        &nbsp;<b>%s</b>&nbsp;<input name="hour" size="2" maxlength="2" value="%s">:<input name="min" size="2" maxlength="2" value="%02d"></td></tr>' % (webmin.text['newfax_sendtime'],curtime[3],curtime[4])
    print '    <tr><td><b>Destination</b> (dialstring)</td><td><input type="text" name="dialstring" size=20 value="%s"></td></tr>' % cgi.escape(dialstring,1)
    print '    <tr><td><b>Addresse</b></td><td><input type=text name="addressee" size=20 value="%s"></td></tr>' % cgi.escape(addressee,1)
    print '    <tr><td><b>Subject</b></td><td><input type=text name="subject" size=80 value="%s"></td></tr>' % cgi.escape(subject,1)
    if formActionType.startswith("forward"):	
	if fjobid==None or fqtype==None:
	    fjobid=""
	    fqtype=""	    
	#print '    <input type="hidden" name="formJobFile" value="%s">' % faxfile
	# the jobid/qtype represent the fax file which will be forwarded, not a new jobid/file for the send queue
	print '    <input type="hidden" name="jobid" value="%s"><input type="hidden" name="qtype" value="%s">' % (fjobid,fqtype)
    else:
	print '    <tr><td><b>Faxfile (*.sff,*.ps,*.pdf)</b></td><td><input type="file" name="upfile"></td></tr>'
    print '    <input type="hidden" name="faxcreate" value="%s">' % formActionType
    print '    <tr><td><input type=SUBMIT value="Send"></td></tr>'
    print '   </table></form>'
    print ' </td></tr>'
    print '</table>'


# check the form values
#def checkform():
    
	


try:
    # get the "POST" vars
    form = cgi.FieldStorage()
    if not form or capifaxwm.checkconfig()==-1:
	capifaxwm.CSConfigError
            
    # check the user (of this proccess) can write to the faxnextfile in the sendq dir
    checkfile=os.path.join(capifaxwm.UsersFax_Path,webmin.remote_user,"sendq",capifaxwm.faxnextfile)
    if os.path.exists(checkfile) and not os.access(checkfile,os.W_OK):    
	raise "NoAccess"
    
    # check post values
    faxcreate = form.getfirst("faxcreate")    
    if not faxcreate:
        faxcreate = "new"

    if faxcreate =="forward":
	qtype=form.getfirst("qtype")
	jobid = form.getfirst("jobid")
	# faxfile = importqfax(jobid,qtype) ## now done after the form is send
	faxfile=""
	formActionType="forwardsend"
	#if not faxfile:
	#    raise capifaxwm.CSConfigError
	shownewform(jobid,qtype)
    elif faxcreate =="new":
	qtype=""
	jobid=""
	faxfile=""
	formActionType="newsend" # TODO just for testing
	shownewform()
    elif faxcreate == "newsend":
	dialstring = form.getfirst("dialstring")	
	subject = form.getfirst("subject")	
	addressee = form.getfirst("addressee")	
	formActionType="newsend"	
	
	if capifaxwm.CheckDialString(dialstring)==-1:
	    print "<p><b> Invalid dailstring </b></p>"	    
            raise capifaxwm.FormInputError
	try:
	    formTime = form.getfirst("year")+"-"+form.getfirst("month")+"-"+form.getfirst("day")+" "+\
		form.getfirst("hour")+":"+form.getfirst("min")	
	    timestruct = time.strptime(formTime,"%Y-%m-%d %H:%M")
	    timec = time.asctime(timestruct)
	except:
	    print "<p><b> Invalid time and/or date </b></p>"	    
            raise capifaxwm.FormInputError	
	
	if form.has_key("upfile"):	    
	    # Security note: if you use python 2.3, change to tempfile.mkstemp
	    # in python version earlier 2.3, mktemp hasn't the option to specify a directory	    
	    newpath=os.path.join(capifaxwm.UsersFax_Path,webmin.remote_user,"sendq")+os.sep
	    tmpjobfile = os.path.basename(tempfile.mktemp(".tempfax.sff")) 	    
	    upfile = form['upfile']
	    if not tmpjobfile or not newpath or not upfile.file :
		print "<p>%s%s - %s</p>" % (newpath,tmpjobfile,cgi.escape(upfile,1))
		raise capifaxwm.CSConfigError
	    # avoid an "@" as filenamestart, which causes trouble in gs
	    tmpjobfile = "ul_"+tmpjobfile #[1:]
	    outFile = open(newpath+tmpjobfile,"wb")
	    outFile.write(upfile.file.read())
	    outFile.close()	    
    	    if not upfile.filename.endswith("sff"):
		t=os.popen("file -b -i "+newpath+tmpjobfile+" 2>/dev/null")
		filetype=t.read()		
		if (t.close()):
		    raise capifaxwm.CSConvError("can't execute program \"file\"")
		fileext=""
		if (re.search("application/postscript",filetype)):
		    fileext="ps"
		elif (re.search("application/pdf",filetype)):
		    fileext="pdf"
		else:
		    print "<p><b> False File format - currently only sff/ps/pdf files are supported </b></p>"	    
        	    raise capifaxwm.FormInputError
		if fileext=="pdf":
		    capifaxwm.ConvertPDF2PS(newpath+tmpjobfile,newpath+"ps_"+tmpjobfile)
		    rmfile(newpath+tmpjobfile)
		    tmpjobfile="ps_"+tmpjobfile
		
		capifaxwm.ConvertPS2SFF(newpath+tmpjobfile,newpath+"out_"+tmpjobfile)
		rmfile(newpath+tmpjobfile)
		tmpjobfile ="out_"+tmpjobfile 		

	    capifaxwm.sendfax(webmin.remote_user,dialstring,newpath+tmpjobfile,timec,addressee,subject)
	    if rmfile(newpath+tmpjobfile)==-1:
		print "<p><b> Failed to remove tempory upload file</b></p>"
	else:	
	    print "<p><b> No file uploaded </b></p>"
	    raise capifaxwm.FormInputError
	
    elif faxcreate =="forwardsend":
	dialstring = form.getfirst("dialstring")	
	subject = form.getfirst("subject")	
	addressee = form.getfirst("addressee")
	# faxfile=form.getfirst("formJobFile") # old version
	formActionType="forwardsend"
		
	if capifaxwm.CheckDialString(dialstring)==-1:
	    print "<p><b> Invalid dailstring </b></p>"	    
            raise capifaxwm.FormInputError

	try:
	    formTime = form.getfirst("year","")+"-"+form.getfirst("month","")+"-"+form.getfirst("day","")+" "+\
		form.getfirst("hour","")+":"+form.getfirst("min","")	
	    timestruct = time.strptime(formTime,"%Y-%m-%d %H:%M")
	    timec = time.asctime(timestruct)
	except:
	    print "<p><b> Invalid time and/or date </b></p>"	    
            raise capifaxwm.FormInputError
	
	fjobid=form.getfirst("jobid")
	fqtype=form.getfirst("qtype")	
	if (not fqtype) or (capifaxwm.CheckJobID(fjobid)==-1):
	    raise capifaxwm.CSConfigError
	
	faxfile = importqfax(fjobid,fqtype)
	if not faxfile:
	    print "<p><b> Forward temp file creation/copy failed</b></p>"
	    raise capifaxwm.CSConfigError

	capifaxwm.sendfax(webmin.remote_user,dialstring,faxfile,timec,addressee,subject)
	if rmfile(faxfile)==-1:
            print "<p><b> Failed to remove tempory upload file</b></p>"

    else:
	# nothing else currently supported
	raise capifaxwm.CSConfigError
    


except capifaxwm.CSConfigError:
    print "<p><b>%s: False settings/config - please start from the main module page<br> and try not to call this page directly</b></p>" % webmin.text.get('error','').upper()
except "NoAccess":
    print "<p><b> You don't have write access to an important file (%s)in your sendq<br>" % capifaxwm.faxnextfile
    print " without the correct permission, you cannot create any new faxes</b></p>"
    print '<p><form METHOD="POST" ACTION="chsendnextnr.cgi"><input type=SUBMIT value="change permission"></form></p>'
except capifaxwm.CSConvError,e:
    print "<p><b>Convert- %s: %s</b></p>" % (webmin.text.get('error','').upper(),cgi.escape(e.message,1))
except capifaxwm.FormInputError:
    shownewform(fjobid,fqtype)
print "<hr>"
webmin.footer([("", "module index")])
