#!/usr/bin/env python
#
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

# Uses functions from/based on CapSuite (cs_helper.py, capisuitefax):
#    copyright            : (C) 2002 by Gernot Hillier
#    email                : gernot@hillier.de
# http://www.capisuite.org

# Uses Webmin-Python Module Written by Peter Astrand (&Aring;strand) <peter@cendio.se>
# Copyright (C) 2002 Cendio Systems AB (http://www.cendio.se)


#
# Coding style: Max linewidth 120 chars, 4 spaces per tab
#


import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser

def abort_error(errmsg):
    print "Content-type: text/html\n"
    sys.stdout.flush()
    print "<html><head><title>Error starting capimin module</title></head><body><p><b> %s</b></p></body></html>" % errmsg
    sys.exit()
    

try:
    import webmin
except:
    abort_error("ERROR: couldn't load Webmin-Python module, not installed?<br>"\
                "See the capimin website for install instructions")
    
try:
    import cs_helpers
except:
    abort_error("ERROR: couldn't load cs_helper module. This is a module provided by CapiSuite<br>\n"\
                "If you have installed multiple python versions, make sure that all cgi files of this module<br>\n"\
                "point to the python version, capisuite uses (see e.g. the program capisuitefax for the path)")

try:
    import wm_pytools,capifaxwm
except:
    abort_error("ERROR: couldn't load capmin modules. capimin wasn't installed correct")


webmin.header(webmin.text['index_title'],image=None,help="intro",config=0,nomodule=1)
#print "Content-type: text/html\n"
sys.stdout.flush()


print "<hr>"
#init capifaxwm module:
if (capifaxwm.capiconfig_init()==-1):
    print "<p><b>%s: Could not read/invalid configuration </b></p>" % webmin.text.get('error','').upper()

print "<br>Users Fax Path: %s" % capifaxwm.listpath['fax_user_dir']
print "<br>Users Voice Path: %s" % capifaxwm.listpath['voice_user_dir']
print "<br>Global Spool Path: %s" % capifaxwm.listpath['spool_dir']



sections=capifaxwm.CAPI_config.sections()
sections.remove('GLOBAL')
sections.sort()
sections.insert(0,'GLOBAL')
# to know the fax permission of each user, we need to know outgoing_MSN from the global section first
#globalFaxoutMsn=capifaxwm.CAPI_config.get('GLOBAL','outgoing_MSN')

print '<hr><p> User list:<br>'
for s in sections:
    if not s=="GLOBAL":
        print '<a href="#%s">[ %s ]</a>&nbsp;&nbsp;' % (s,s)    
print '</p>'

# print '<p> =========  <b>Print configuration</b> ===================</p>'

for s in sections:
    print '<br><a name="%s"><table border="1">'  % s
    print ' <tr bgcolor=#%s><th>[ %s ]</th></tr>  ' % (webmin.tb,s)
    print ' <tr bgcolor=#%s><td>\n  <table border="1" cellspacing="0">' % webmin.cb    
    for o in capifaxwm.CAPI_config.options(s):
        value=capifaxwm.CAPI_config.get(s,o)
        print '   <tr><td>%s&nbsp;</td><td>&nbsp;%s</td></tr>' % (o,value)

    if not s=="GLOBAL":
        # check voice permissions
        print '  <tr><td>Voice calls</td><td>'
        if capifaxwm.CAPI_config.has_option(s,'voice_numbers'):
            if cs_helpers.getOption(capifaxwm.CAPI_config,s,'voice_action'):
                print "&nbsp;yes"
            else:
                print "&nbsp;Error: Voicenumber definied but manditory 'voice_action' is missing!<br>"\
                      "&nbsp;unless you haven\'t customized your capsuite scrips, voice call feature is disabled"
        else:
            print "&nbsp;no"
        print '</td></tr>'
        # check fax permissions        
        
        faxOutMsn=cs_helpers.getOption(capifaxwm.CAPI_config,s,'outgoing_MSN')
        faxNumbers=cs_helpers.getOption(capifaxwm.CAPI_config,s,'fax_numbers')
        if not faxOutMsn and not faxNumbers:
            print '  <tr><td>Fax out</td><td>&nbsp;no</td></tr>'
            print '  <tr><td>Fax in</td><td>&nbsp;no</td></tr>'            
        elif not faxNumbers and faxOutMsn:
            print '  <tr><td>Fax out</td><td>&nbsp;yes (on MSN %s )</td></tr>' % faxOutMsn
            print '  <tr><td>Fax in</td><td>&nbsp;no</td></tr>'    
        else:
            if not cs_helpers.getOption(capifaxwm.CAPI_config,s,'fax_action'):
                print '  <tr><td colspan="2">'
                print '<p><b> ERROR</b>: manditory "fax_action" is missing! unless you haven\'t customized your capsuite<br>'\
                      ' scripts the CapiSuite fax config as printed below will NOT work!</p>'
                print '</td></tr>'
            print '  <tr><td>Fax out</td><td>&nbsp;yes</td></tr>'
            print '  <tr><td>Fax in</td><td>&nbsp;yes</td></tr>'   
            print '  <tr><td colspan="2">'
            if faxOutMsn:
                print 'Outgoing faxes will be send with the number %s, the user can receive faxes on the<br> '\
                      'in "fax_numbers" listed number(s)' % faxOutMsn
            else:
                print 'Outgoing faxes will be send with the first number (MSN) from "fax_numbers", the user can<br>'\
                      ' receive faxes on the in "fax_numbers" listed number(s) ("*"= receive on all MSNs)'
            print '</td></tr>'
            
    print '  </table>\n </td></tr></table>'

    
print "<p>&nbsp;</p><hr>"       
webmin.footer([("/", "index")])

