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

#
# Coding style: Max linewidth 120 chars, 4 spaces per tab
# 



import webmin
import os, re, time, string
import cs_helpers, capifaxwm
import urllib

capifaxwm.capiconfig_init()


    
# !!!!!!!! OLD FUNCTION (V II) - SEE BELOW FOR NEW !!!!!!!!!!!!!!!!!!!!
# (still in active code for testing/ verifying)
def ShowSend2(user,changepage="change.cgi",formname=""):    
    if (capifaxwm.checkconfig() == -1) or (capifaxwm.checkfaxuser(user,1) == 0) or not changepage:
        raise capifaxwm.CSConfigError
    
    cslist = "faxsend"
    if not formname:
        formname=cslist

    sendq=capifaxwm.UsersFax_Path    
    sendq=os.path.join(sendq,user,"sendq")+"/"
    #print '<p><b> %s: %s</b></p>' % (webmin.text['csfax_user'],user)
    print '<!-- ================== Show OLD-New (VII) Send queue =================== -->'
    print '<form action=%s method=post name=%s>' % (changepage,formname)
    print '<table border="1">\n <tr bgcolor=#%s>' % webmin.tb
    print '   <th>&nbsp;</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th>' %\
                        (webmin.text['index_id'],webmin.text['index_dialstring'],
                         webmin.text['index_addressee'],webmin.text['index_tries'])
    print '   <th>%s</th><th>%s</th><th><b>&nbsp;</b></th>\n </tr>' % (webmin.text['index_nexttry'],
                                                                       webmin.text['index_subject'])
    
    files=os.listdir(sendq)
    files=filter (lambda s: re.match("fax-.*\.txt",s),files)
    cindex=0
    for job in files:
        
        control=cs_helpers.readConfig(sendq+job)
        jobid = re.match("fax-([0-9]+)\.txt",job).group(1)
        starttime=(time.strptime(control.get("GLOBAL","starttime")))[0:8]+(-1,)
        # the filetype detections is done, because change.cgi does (currently) not reread the jobfile
        # (it wasn't needed, but since there can be color files...).
        datafile = control.get("GLOBAL","filename")
        if datafile==None: datafile="" # to avoid exception with splittext, check done below with filetype
        filetype = os.path.splitext(datafile)[1].lower()[1:] # splittext returns a list of 2, so no "None" check needed
        if not filetype:
            print "<p><b> %s: No or invalid job data-filename found int job %s </b></p>" %\
                          (webmin.text.get('error','').upper(),jobid)
            raise capifaxwm.CSConfigError
    

        print ' <tr bgcolor=#%s>' % webmin.cb
        print '   <td><input type=checkbox name="cindex" value="%s"></td>' % cindex
        print "   <td>&nbsp;%s</td>" % jobid
        print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","dialstring")
        print '   <td><input TYPE="TEXT" NAME="formDialAddressee_%s" SIZE="15" MAXLENGTH="40" value="%s"></td>' %\
                              (cindex,cs_helpers.getOption(control,"GLOBAL","addressee",""))
        print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","tries")
    
        print '   <td nowrap><input name="year_%s" type="text" size="4" maxlength="4" value="%s">-<select'\
              ' name="month_%s">' % (cindex,starttime[0],cindex)
        for i in range(1,13):
            selected =""
            if i==starttime[1]:
                selected=' selected="selected"'
            print '        <option value="%s"%s>%s</option>' % (i,selected,webmin.text["smonth_"+str(i)])
        print '      </select>-<input name="day_%s" size="2" maxlength="2" value="%s">' % (cindex,starttime[2])
        print '        &nbsp;&nbsp;<input name="hour_%s" size="2" maxlength="2" value="%s">:<input name="min_%s"'\
              ' size="2" maxlength="2" value="%02d"></td>' % (cindex,starttime[3],cindex,starttime[4])
        #print '   <td><input TYPE="TEXT" NAME="datetime" SIZE="8" MAXLENGTH="12" value="'+time1+'">'
        #print '       <input TYPE="TEXT" NAME="date" SIZE="10" MAXLENGTH="16" value="'+time2+'"></td>'
    
        print '   <td><input type="TEXT" name="formSubject_%s" SIZE="30" MAXLENGTH="40" value="%s"></td>' %\
                      (cindex,cs_helpers.getOption(control,"GLOBAL","subject",""))
        print '   <input type="hidden" name="cjobid" value="%s">' % jobid
        print '   <input type="hidden" name="formDialString" value="%s">' % control.get("GLOBAL","dialstring")
        print '   <input type="hidden" name="formTries" value="%s">' % control.get("GLOBAL","tries")
        print '   <input type="hidden" name="formOrgDate" value="%s">' % control.get("GLOBAL","starttime")
        print '   <input type="hidden" name="filetype" value="%s">' % filetype
        #print '   <td><input type=submit name="schange" value="%s"></td>' % webmin.text['index_change']
        print '<td>&nbsp;</td>'
        print ' </tr>'
        cindex=cindex+1

    print "</table>"
    
    print '<input type="hidden" name="cslist" value="%s">' % cslist
    # java script code to select / invert select the checkboxes
    print "<a href='' onClick='document.forms[\"%s\"].cindex.checked = true;"\
          " for(i=0; i<document.forms[\"%s\"].cindex.length; i++) { document.forms[\"%s\"].cindex[i].checked ="\
          " true; } return false'>%s</a>" % (formname,formname,formname,webmin.text['list_all'])
    print "&nbsp;&nbsp;<a href='' onClick='document.forms[\"%s\"].cindex.checked ="\
          " !document.forms[\"%s\"].cindex.checked; for(i=0; i<document.forms[\"%s\"].cindex.length; i++)"\
          " { document.forms[\"%s\"].cindex[i].checked = !document.forms[\"%s\"].cindex[i].checked; }"\
          " return false'>%s</a>"  % (formname,formname,formname,formname,formname,webmin.text['list_invert'])
    # submit buttons
    print '<br><br><input type=submit name="change" value="%s">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'\
          '<input type=submit name="onehlater" value="1h later">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'\
          '<input type=submit name="delete" value="%s"></form>' % (webmin.text['index_change'],webmin.text['delete'])
    
    print '<!-- END================ Show OLD-New (VII) Send queue =================== -->'

def ShowSend3(user,changepage="change.cgi",formname=""):    
    if (capifaxwm.checkconfig() == -1) or (capifaxwm.checkfaxuser(user,1) == 0) or not changepage:
        raise capifaxwm.CSConfigError
    
    cslist = "faxsend"
    if not formname:
        formname=cslist

    sendq=capifaxwm.UsersFax_Path    
    sendq=os.path.join(sendq,user,"sendq")+"/"
    #print '<p><b> %s: %s</b></p>' % (webmin.text['csfax_user'],user)
    print '<!-- ================== Show Send queue V III =================== -->'    
    print '<form action=%s method=post name=%s>' % (changepage,formname)
    print '<table border="1">\n <tr bgcolor=#%s>' % webmin.tb
    print '   <th>&nbsp;</th><th>%s</th><th>%s</th><th>%s</th><th>%s</th>' %\
                        (webmin.text['index_id'],webmin.text['index_dialstring'],
                         webmin.text['index_addressee'],webmin.text['index_tries'])
    print '   <th>%s</th><th>%s</th><th><b>&nbsp;</b></th>\n </tr>' % (webmin.text['index_nexttry'],
                                                                       webmin.text['index_subject'])
    
    files=os.listdir(sendq)
    files=filter (lambda s: re.match("fax-.*\.txt",s),files)
    cindex=0
    for job in files:
        
        control=cs_helpers.readConfig(sendq+job)
        jobid = re.match("fax-([0-9]+)\.txt",job).group(1)
        starttime=(time.strptime(control.get("GLOBAL","starttime")))[0:8]+(-1,)
        # the filetype detections is done, because change.cgi does (currently) not reread the jobfile
        # (it wasn't needed, but since there can be color files...).
        datafile = control.get("GLOBAL","filename")
        if datafile==None: datafile="" # to avoid exception with splittext, check done below with filetype
        filetype = os.path.splitext(datafile)[1].lower()[1:] # splittext returns a list of 2, so no "None" check needed
        if not filetype:
            print "<p><b> %s: No or invalid job data-filename found int job %s </b></p>" %\
                          (webmin.text.get('error','').upper(),jobid)
            raise capifaxwm.CSConfigError
    

        print ' <tr bgcolor=#%s>' % webmin.cb
        print '   <td><input type=checkbox name="cindex" value="%s"></td>' % cindex
        print "   <td>&nbsp;%s</td>" % jobid
        print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","dialstring")
        print '   <td><input TYPE="TEXT" NAME="formDialAddressee_%s" SIZE="15" MAXLENGTH="40" value="%s"></td>' %\
                              (cindex,cs_helpers.getOption(control,"GLOBAL","addressee",""))
        print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","tries")
    
        print '   <td nowrap><input name="year_%s" type="text" size="4" maxlength="4" value="%s">-<select'\
              ' name="month_%s">' % (cindex,starttime[0],cindex)
        for i in range(1,13):
            selected =""
            if i==starttime[1]:
                selected=' selected="selected"'
            print '        <option value="%s"%s>%s</option>' % (i,selected,webmin.text["smonth_"+str(i)])
        print '      </select>-<input name="day_%s" size="2" maxlength="2" value="%s">' % (cindex,starttime[2])
        print '        &nbsp;&nbsp;<input name="hour_%s" size="2" maxlength="2" value="%s">:<input name="min_%s"'\
              ' size="2" maxlength="2" value="%02d"></td>' % (cindex,starttime[3],cindex,starttime[4])
  
        print '   <td><input type="TEXT" name="formSubject_%s" SIZE="30" MAXLENGTH="40" value="%s"></td>' %\
                      (cindex,cs_helpers.getOption(control,"GLOBAL","subject",""))

        print '   <input type="hidden" name="cjobid" value="%s">' % jobid
        #print '   <td><input type=submit name="schange" value="%s"></td>' % webmin.text['index_change']
        print '<td>&nbsp;</td>'
        print ' </tr>'
        cindex=cindex+1

    print "</table>"
    
    print '<input type="hidden" name="cslist" value="%s">' % cslist
    # java script code to select / invert select the checkboxes
    print "<a href='' onClick='document.forms[\"%s\"].cindex.checked = true;"\
          " for(i=0; i<document.forms[\"%s\"].cindex.length; i++) { document.forms[\"%s\"].cindex[i].checked ="\
          " true; } return false'>%s</a>" % (formname,formname,formname,webmin.text['list_all'])
    print "&nbsp;&nbsp;<a href='' onClick='document.forms[\"%s\"].cindex.checked ="\
          " !document.forms[\"%s\"].cindex.checked; for(i=0; i<document.forms[\"%s\"].cindex.length; i++)"\
          " { document.forms[\"%s\"].cindex[i].checked = !document.forms[\"%s\"].cindex[i].checked; }"\
          " return false'>%s</a>"  % (formname,formname,formname,formname,formname,webmin.text['list_invert'])
    print '&nbsp;&nbsp;%s' % webmin.hlink("Help","sendlist")
    # submit buttons
    print '<br><br>'
    print '<input type=submit name="change" value="%s">&nbsp;<input type=submit name="changsend" value="%s">&nbsp;'\
          '<input type=submit name="onehlater" value="%s">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'\
          '<input type=submit name="delete" value="%s"></form>' % \
          (webmin.text['index_change'],webmin.text['index_chnagesend'],webmin.text['index_1hlater'],
           webmin.text['delete'])
    
    print '<!-- END================ Show New Send queue V III=================== -->'

# List received list for fax and voice calls
# fileprefix can be "fax" or "voice". this is also used to get the right dir path
def ShowReceived(user,fileprefix="fax",forwardopt=0,newpage="newfax.cgi",dldpage="",removepage="",formname=""):
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
    if not formname:
        formname=qtype
    
    print '<!-- ================== Show a received list =================== -->'
    
    path=os.path.join(path,user,"received")+"/"
    if removepage:
        print '<form action=%s method=post name=%s>' % (removepage,formname)
    print '<table border="1">\n <tr bgcolor=#%s>' % webmin.tb
    if removepage:
        print '   <th>&nbsp;</th>' 
    print '   <th>%s</th><th>From</th><th>To (MSN)</th><th>Time</th><th>%s</th>' %\
            (webmin.text['index_id'],webmin.hlink("ISDN cause","list_isdn_cause"))
    if forwardopt==1 and newpage:
        print '   <th>&nbsp;</td>'
    print ' </tr>'
    
    if not os.path.exists(path):
        print "</table>"
        return    
    files=os.listdir(path)
    files=filter (lambda s: re.match(fileprefix+"-.*\.txt",s),files)

    for job in files:
        print ' <tr bgcolor=#%s>' % webmin.cb
        control=cs_helpers.readConfig(path+job)
        jobid = re.match(fileprefix+"-([0-9]+)\.txt",job).group(1)
        if removepage:
            print '   <td><input type=checkbox name="cjobid" value=%s></td>' % jobid
        print "  <td>&nbsp;%s</td>" % jobid
        callerid=control.get("GLOBAL","call_from")
        if callerid=="" or callerid=="-":
            callerid=webmin.text['csfax_nocallerid']
        if dldpage:
            urlparams = urllib.urlencode({'jobid': jobid, 'qtype': qtype})
            print '   <td>&nbsp;<a href="%s?%s">%s</a></td>' % (dldpage,urlparams,callerid)
        else:
            print "  <td>&nbsp;%s</td>" % callerid
        print "  <td>&nbsp;%s</td>" % control.get("GLOBAL","call_to")
        print "  <td nowrap>&nbsp;%s</td>" % control.get("GLOBAL","time")
        print "  <td>&nbsp;%s</td>" % control.get("GLOBAL","cause")

        if forwardopt==1:
            urlparams = urllib.urlencode({'jobid': jobid, 'qtype': 'faxreceived', 'faxcreate' : 'forward'})
            print '   <td><b><a href="%s?%s">%s</a></b></td>' % (newpage,urlparams,webmin.text['index_forward'])

#       print "  <td>&nbsp;%s</td>" % control.get("GLOBAL","filename") # TODO?:change it to file name only

        print "</tr>"
    print "</table>"
    print '<input type="hidden" name="cslist" value="%s">' % qtype
    # java script code to select / invert select the checkboxes
    print "<a href='' onClick='document.forms[\"%s\"].cjobid.checked = true;"\
          " for(i=0; i<document.forms[\"%s\"].cjobid.length; i++) { document.forms[\"%s\"].cjobid[i].checked ="\
          " true; } return false'>%s</a>" % (formname,formname,formname,webmin.text['list_all'])
    print "&nbsp;&nbsp;<a href='' onClick='document.forms[\"%s\"].cjobid.checked ="\
          " !document.forms[\"%s\"].cjobid.checked; for(i=0; i<document.forms[\"%s\"].cjobid.length; i++)"\
          " { document.forms[\"%s\"].cjobid[i].checked = !document.forms[\"%s\"].cjobid[i].checked; }"\
          " return false'>%s</a>"  % (formname,formname,formname,formname,formname,webmin.text['list_invert'])
    print '<br><br><input type=submit name=delete value="%s">' % webmin.text['delete']
#    if forwardopt==1:
#        print '<input type="hidden" name="faxcreate" value="forward">
#        print '&nbsp;&nbsp;&nbsp;<input type=submit name=forward value="%s">' % webmin.text['index_forward'
    print '</form>'

    print '<!-- END=============== Show a received list =================== -->'

# Show Done/Failed dir for the current user
def ShowGlobal(user,cslist="faxdone",newpage="",dldpage="",removepage="",formname=""):
    if (capifaxwm.checkconfig() == -1) or (capifaxwm.checkfaxuser(user,1) == 0):
        raise capifaxwm.CSConfigError
    
    if not capifaxwm.listtypes.has_key(cslist) or (cslist!="faxfailed" and cslist!="faxdone"):
        raise capifaxwm.CSConfigError
    if not formname:
        formname=cslist
    
    print '<!-- ================== Show a global list =================== -->'
    
    path=capifaxwm.BuildListPath(cslist)
    if removepage:
        print '<form action=%s method=post name=%s>' % (removepage,formname)
    print '<table border="1">\n <tr bgcolor=#%s>' % webmin.tb
    if removepage:
        print '   <th>&nbsp;</th>' 
    print '   <th>%s</th><th>%s</th><th>%s</th><th>%s</th>' %\
          (webmin.text['index_id'],webmin.text['index_dialstring'],webmin.text['index_addressee'],
           webmin.text['index_tries'])
    print '   <th>Time</th><th>%s</th>' % webmin.text['index_subject']
    print ' </tr>'
    
    fileprefix =""
    if capifaxwm.listtypes[cslist][1]==1:
        fileprefix=user+"-"
    fileprefix=fileprefix+capifaxwm.listtypes[cslist][0]+"-"
    
    if not os.path.exists(path):
        print "</table>"
        return    
    files=os.listdir(path)
    files=filter (lambda s: re.match(fileprefix+".*\.txt",s),files)
    for job in files:
        control=cs_helpers.readConfig(path+job)
        jobid = re.match(fileprefix+"([0-9]+)\.txt",job).group(1)

        print ' <tr bgcolor=#%s>' % webmin.cb
        if removepage:
            print '   <td><input type=checkbox name="cjobid" value=%s></td>' % jobid
        print "   <td>&nbsp;%s</td>" % jobid
        print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","dialstring")
        print '   <td>&nbsp;%s</td>' % cs_helpers.getOption(control,"GLOBAL","addressee","")
        print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","tries")
        print "   <td>&nbsp;%s</td>" % control.get("GLOBAL","starttime")

        print '   <td>&nbsp;%s</td>' % cs_helpers.getOption(control,"GLOBAL","subject","")
    print "</table>"
    print '<input type="hidden" name="cslist" value="%s">' % cslist

    # java script code to select / invert select the checkboxes
    print "<a href='' onClick='document.forms[\"%s\"].cjobid.checked = true;"\
          " for(i=0; i<document.forms[\"%s\"].cjobid.length; i++) { document.forms[\"%s\"].cjobid[i].checked ="\
          " true; } return false'>%s</a>" % (formname,formname,formname,webmin.text['list_all'])
    print "&nbsp;&nbsp;<a href='' onClick='document.forms[\"%s\"].cjobid.checked ="\
          " !document.forms[\"%s\"].cjobid.checked; for(i=0; i<document.forms[\"%s\"].cjobid.length; i++)"\
          " { document.forms[\"%s\"].cjobid[i].checked = !document.forms[\"%s\"].cjobid[i].checked; }"\
          " return false'>%s</a>"  % (formname,formname,formname,formname,formname,webmin.text['list_invert'])

    print '<br><br><input type=submit name=delete value="%s"></form>' % webmin.text['delete']

    print '<!-- END=============== Show a global list =================== -->'
