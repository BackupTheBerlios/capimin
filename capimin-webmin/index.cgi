#!/usr/bin/python

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
    abort_error("Error, couldn't load Webmin-Python module, not installed?<br>See the capimin website for install instructions")
    
try:
    import cs_helpers
except:
    abort_error("Error, couldn't load cs_helper module. This is a module provided by CapiSuite")

try:
    import wm_pytools,capifaxwm
except:
    abort_error("Error, couldn't load capmin modules. capimin wasn't installed correct")


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

print '<p> =========  <b>Print configuration</b> ===================</p>'

sections=capifaxwm.CAPI_config.sections()
sections.remove('GLOBAL')
sections.sort()
sections.insert(0,'GLOBAL')
# to know the fax permission of each user, we need to know outgoing_MSN from the global section first
#globalFaxoutMsn=capifaxwm.CAPI_config.get('GLOBAL','outgoing_MSN')


for s in sections:
    print '<br><table border="1">' 
    print ' <tr bgcolor=#%s><th>[ %s ]</th></tr>  ' % (webmin.tb,s)
    print ' <tr bgcolor=#%s><td>\n  <table border="1" cellspacing="0">' % webmin.cb    
    for o in capifaxwm.CAPI_config.options(s):
        value=capifaxwm.CAPI_config.get(s,o)
        print '   <tr><td>%s&nbsp;</td><td>&nbsp;%s</td></tr>' % (o,value)

    if not s=="GLOBAL":
        # check voice permissions
        print '  <tr><td colspan="2"><b>'
        if capifaxwm.CAPI_config.has_option(s,'voice_numbers'):
            if cs_helpers.getOption(capifaxwm.CAPI_config,s,'voice_action'):
                print " User can receive voice calls"
            else:
                print " Error: Voicenumber definied but manditory 'voice_action' is missing!<br>"\
                      " unless you haven\'t customized your capsuite scrips, voice call feature is disabled"
        else:
            print " Voice calls are not enabled for this user"
        print '</b></tr></td>'
        # check fax permissions
        bEnd="</b>"
        print '  <tr><td colspan="2"><b>'
        faxOutMsn=cs_helpers.getOption(capifaxwm.CAPI_config,s,'outgoing_MSN')
        faxNumbers=cs_helpers.getOption(capifaxwm.CAPI_config,s,'fax_numbers')
        if not faxOutMsn and not faxNumbers:
            print " sending and receiving faxes is not enabled for this user"
        elif not faxNumbers and faxOutMsn:
            print " only sending faxes is enabled for this user (using number: %s ) " % faxOutMsn
        else:
            if not cs_helpers.getOption(capifaxwm.CAPI_config,s,'fax_action'):
                print '<p> ERROR: manditory "fax_action" is missing! unless you haven\'t customized your capsuite<br>'\
                      ' scripts the CapiSuite fax config as printed below will NOT work!</p></b>'
                bEnd=""
            print " sending and receiving faxes is enabled for this user<br> "
            if faxOutMsn:
                print 'Outfaxes will be send with the number %s, the user can receive faxes on the<br> '\
                      'in "fax_numbers" listed number(s)' % faxOutMsn
            else:
                print 'Outfaxes will be send with first number (MSN) from "fax_numbers", the user can<br>'\
                      ' receive faxes on the in "fax_numbers" listed number(s) ("*"= receive on all MSNs)'
        print '%s</tr></td>' % bEnd
            
    print '  </table>\n </td></tr></table>'

    
print "<p>&nbsp;</p><hr>"       
webmin.footer([("/", "index")])

