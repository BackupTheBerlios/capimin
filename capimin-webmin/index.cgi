#!/usr/bin/python

import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
import webmin
import cs_helpers,wm_pytools,capifaxwm


webmin.header(webmin.text['index_title'],image=None,help="intro",config=1,nomodule=1)
#print "Content-type: text/html\n"
sys.stdout.flush()


print "<hr>"
#init capifaxwm module:
if (capifaxwm.capiconfig_init()==-1):
    print "<p><b>%s: Could not read/invalid configuration </b></p>" % webmin.text.get('error','').upper()

print "<br>Users Fax Path: %s" % capifaxwm.listpath['fax_user_dir']
print "<br>Users Voice Path: %s" % capifaxwm.listpath['voice_user_dir']
print "<br>Global Spool Path: %s" % capifaxwm.listpath['spool_dir']

print '<p> =========  <b>Print configuration</b> ===================</p>'

sections=capifaxwm.CAPI_config.sections()
sections.remove('GLOBAL')
sections.sort()
sections.insert(0,'GLOBAL')
for s in sections:
    print '<br><table border="1">' 
    print ' <tr bgcolor=#%s><th>[ %s ]</th></tr>  ' % (webmin.tb,s)
    print ' <tr bgcolor=#%s><td>\n  <table border="1" cellspacing="0">' % webmin.cb
    for o in capifaxwm.CAPI_config.options(s):
        value=capifaxwm.CAPI_config.get(s,o)
        print '   <tr><td>%s&nbsp;</td><td>&nbsp;%s</td></tr>' % (o,value)

    if not s=="GLOBAL":
        print '  <tr><td colspan="2"><b>'
        if capifaxwm.CAPI_config.has_option(s,'voice_numbers'):
            if capifaxwm.CAPI_config.has_option(s,'voice_action'):
                print " User can receive voice calls"
            else:
                print " Error: Voicenumber definied but manditory 'voice_action' missing"\
                      " check you config file"
        else:
            print " Voice calls are not enabled for this user"
        print '</b></tr></td>'

    print '  </table>\n </td></tr></table>'

    
print "<p>&nbsp;</p><hr>"       
webmin.footer([("/", "index")])

