# Based on the list function from:
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
#
# for the rest: http://capimin.berlios.de email: cibi@users.berlios.de


import webmin
import os, re, time, string
import cs_helpers, capifaxwm

capifaxwm.capiconfig_init()


def ShowSend(user,changepage="change.cgi",abortpage="abort.cgi"):    
    if (capifaxwm.checkconfig() == -1) or (capifaxwm.checkfaxuser(user,1) == 0):
	raise capifaxwm.CSConfigError
	
    sendq=capifaxwm.UsersFax_Path    
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
def ShowReceived(user,fileprefix="fax",forwardopt=0,newpage="newfax.cgi",dldpage="",removepage=""):
    if (capifaxwm.checkconfig(fileprefix) == -1) or (capifaxwm.checkfaxuser(user,1) == 0):
        raise capifaxwm.CSConfigError
    
    path=""
    qtype=""
    if fileprefix =="fax":
	path = capifaxwm.UsersFax_Path	
	qtype = "faxreceived"
    elif fileprefix == "voice":
	path = capifaxwm.UsersVoice_Path
	qtype = "voicereceived"
    else:
	raise capifaxwm.CSConfigError
        
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

# Show Done/Failed dir for the current user
def ShowGlobal(user,cslist="faxdone",removepage=""):
    if (capifaxwm.checkconfig() == -1) or (capifaxwm.checkfaxuser(user,1) == 0):
        raise capifaxwm.CSConfigError
    
    if not capifaxwm.listtypes.has_key(cslist) or (cslist!="faxfailed" and cslist!="faxdone"):
	raise capifaxwm.CSConfigError

    path=capifaxwm.BuildListPath(cslist)

    print '<table border="1">\n <tr bgcolor=#%s>' % webmin.tb
    print '   <th>%s</th><th>%s</th><th>%s</th><th>%s</th>' %  (webmin.text['index_id'],webmin.text['index_dialstring'],webmin.text['index_addressee'],webmin.text['index_tries'])
    print '   <th>Time</th><th>%s</th>' % webmin.text['index_subject']
    if removepage:
	print '   <th>%s</th>' % webmin.text['delete']
    print ' </tr>'
    
    fileprefix =""
    if capifaxwm.listtypes[cslist][1]==1:
	fileprefix=user+"-"
    fileprefix=fileprefix+capifaxwm.listtypes[cslist][0]+"-"
    files=os.listdir(path)
    files=filter (lambda s: re.match(fileprefix+".*\.txt",s),files)

    for job in files:
	control=cs_helpers.readConfig(path+job)
	jobid = re.match(fileprefix+"([0-9]+)\.txt",job).group(1)

	print ' <tr bgcolor=#%s>' % webmin.cb	
        print "   <td>&nbsp;%s</td>" % jobid
	print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","dialstring")
	print '   <td>&nbsp;%s</td>' % cs_helpers.getOption(control,"GLOBAL","addressee","")
	print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","tries")
	print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","starttime")
	
	print '   <td>&nbsp;%s</td>' % cs_helpers.getOption(control,"GLOBAL","subject","")
	if removepage:
	    print '   <td>&nbsp;&nbsp;<i><a href="%s?jobid=%s&qtype=%s"">%s</a></i></td>' % (removepage,jobid,cslist,webmin.text['delete'])
	print ' </tr>'


    print "</table>"
