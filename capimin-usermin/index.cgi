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

# Uses functions from CapSuite (cs_helper.py, capisuitefax):
#    copyright            : (C) 2002 by Gernot Hillier
#    email                : gernot@hillier.de
#    version              : $Revision: 1.26 $
# http://www.capisuite.de

# Uses Webmin-Python Module Written by Peter Astrand (&Aring;strand) <peter@cendio.se>
# Copyright (C) 2002 Cendio Systems AB (http://www.cendio.se)


#
# Coding style: Max linewidth 120 chars, 4 spaces per tab
# 

import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
import webmin
import cs_helpers,capifaxwm,capimin_lists,wm_pytools

capifaxwm.SwitchAndLoadConifg()


webmin.header(webmin.text['index_title'],image=None,help="intro",config=1,nomodule=1)

sys.stdout.flush()


print "<hr>"
#init capifaxwm module:
if (capifaxwm.capiconfig_init()==-1):
    print "<p><b>%s: Could not read/invalid configuration </b></p>" % webmin.text.get('error','').upper()
elif (capifaxwm.checkfaxuser(webmin.remote_user)==0):
    print '<p><b>%s: user "%s" is not a valid capisuite fax user<br> Your Webmin/Usermin name must match a capisuite'\
          ' fax user (= *nix user) </b></p>' % (webmin.text.get('error','').upper(),webmin.remote_user)
else:
    print '<form action="newfax.cgi" method="POST"><input type="hidden" name="faxcreate" value="new"><input'\
          ' type=SUBMIT value="%s"></form>' % webmin.text['index_newfax']
    print '\n<hr>\n'

    remove_gdirs = wm_pytools.ExtractIntConfig(webmin.config.get('remove_gdirs'),0,0,1)
    
    show_lists = webmin.userconfig.get('show_list',[0,1,2,3,4]).split(',',5)

    for ls in show_lists:
        l=int(ls)
        if l==0:
            print "<p><b> %s </b></p>" % webmin.hlink(webmin.text['index_sendq_title'],"sendlist")
            capimin_lists.ShowSend3(webmin.remote_user)
            print "<hr>"
        elif l==1:
            print "<p><b> Received List: Fax</b></p>"
            capimin_lists.ShowReceived(webmin.remote_user,forwardopt=1,dldpage="download.cgi",removepage="delete.cgi")
            print "<hr>"
        elif l==2 and capifaxwm.checkconfig("voice")!=-1:
            print "<p><b> Received List: Voice</b></p>"
            capimin_lists.ShowReceived(webmin.remote_user,fileprefix="voice",dldpage="download.cgi",
                                       removepage="delete.cgi")
            print "<hr>"
        elif l==3:
            print "<p><b> Done List: Fax</b></p>"
            capimin_lists.ShowGlobal(webmin.remote_user,"faxdone",removepage="delete.cgi")
            print "<hr>"
        elif l==4:
            print "<p><b> Failed List: Fax</b></p>"
            capimin_lists.ShowGlobal(webmin.remote_user,"faxfailed",removepage="delete.cgi")
            print "<hr>"
        else:
            print "<p> Invalid show_list option or list or queue unknown - listening stopped </p>"
            break

#print "<p>&nbsp;</p><hr>"       
webmin.footer([("/", "index")])

