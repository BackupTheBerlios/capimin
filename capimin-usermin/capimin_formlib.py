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
# Coding style: Max linewidth 120 chars
#
# 

import webmin
import time, string, cgi
import capifaxwm


#capifaxwm.capiconfig_init()

def FormTime2CSTime(formtime):
    """Convert time provided (e.g.) by a form to the CapiSuite format
        formtime sample "2005-1-29 2:21"
        return value is genderated by time.asctime(..) sample: "Sat Jan 29 02:21:00 2005"
            which is used by capisuite in the jobfiles
    """
    try:
        timestruct = time.strptime(formtime,"%Y-%m-%d %H:%M")
        cstime = time.asctime(timestruct)
    except:
        raise capifaxwm.CSUserInputError("Invalid time and/or date from Formdata")
    return cstime

# internal function
def __form_change_singlejob(user,formdata):
    
 
    formTime = formdata.getfirst("year","")+"-"+formdata.getfirst("month","")+"-"+formdata.getfirst("day","")+" "+\
                formdata.getfirst("hour","")+":"+formdata.getfirst("min","")
    jtime=FormTime2CSTime(formTime)       
    subject = formdata.getfirst("formSubject","")
    addressee = formdata.getfirst("formDialAddressee","")
    dialstring = formdata.getfirst("formDialString")
    jtries = formdata.getfirst("formTries")
    cjobid = formdata.getfirst("cjobid")
    filetype = formdata.getfirst("filetype")
    cslist = formdata.getfirst("cslist")

    capifaxwm.change_job(user,cjobid,cslist,dialstring,filetype,jtime,addressee,subject,jtries)


def FormChangeJob(user,formdata):
    if (not formdata) or (capifaxwm.checkconfig() == -1) or (capifaxwm.checkfaxuser(user,1) == 0):
        raise capifaxwm.CSConfigError
    if (not formdata.has_key("cindex")) or (not formdata.has_key("cjobid")) or \
        (not formdata.has_key("formDialString")) or (not formdata.has_key("formOrgDate")) or \
        (not formdata.has_key("formTries")) or (not formdata.has_key("filetype")) or \
        (not formdata.has_key("cslist")):
        raise capifaxwm.CSConfigError
      
    if not isinstance(formdata.getvalue("cjobid"),list):
        __form_change_singlejob(user,formdata)
        return
    
    #TODO check listtypes
    alllen=len(formdata.getlist("cjobid"))
    cslist = formdata.getfirst("cslist")
        
    formjoblist = formdata.getvalue("cindex")
    if not isinstance(formjoblist, list):
        formjoblist = [formjoblist] # ;)
    cjobid=None
    for job in formjoblist:
        try:
            cindex=int(job)
            print "<br> cindex %s / %s<br>" % (cindex,alllen)
            if cindex==None or cindex>=alllen or cindex<0:
                print "overflow"
                raise capifaxwm.CSConfigError
            cjobid = formdata["cjobid"][cindex].value
            print "<br>"+cjobid
            formTime = formdata["year"][cindex].value+"-"+formdata["month"][cindex].value+"-"+\
                       formdata["day"][cindex].value+" "+formdata["hour"][cindex].value+":"+\
                       formdata["min"][cindex].value
            jtime=FormTime2CSTime(formTime)
            subject = formdata["formSubject"][cindex].value
            addressee = formdata["formDialAddressee"][cindex].value
            dialstring = formdata["formDialString"][cindex].value
            jtries = formdata["formTries"][cindex].value
            
            filetype = formdata["filetype"][cindex].value            
            
            capifaxwm.change_job(user,cjobid,cslist,dialstring,filetype,jtime,addressee,subject,jtries)
            
        except:
            #local_header()
            print "<br><b>%s:  - JobID: %s</b><br>" %(webmin.text.get('error','').upper(),cjobid)
        
    
