#!/usr/bin/python
# -*-Python-*-


import sys
sys.path.append("..")
sys.stderr = sys.stdout # Send errors to browser
import webmin
import capifaxwm
import cs_helpers,os, re,getopt

webmin.header(webmin.text['index_title'], None, None,0,1)

sys.stdout.flush()
webmin.init_config()

print "<hr>"
#init capifaxwm module:
capifaxwm.capiconfig_init()
if (capifaxwm.UsersFax_Path==None):
    print "<p><b>%s: option fax_user_dir not set in fax configuration</b></p>" % webmin.text['error'].upper()
elif (capifaxwm.checkfaxuser(webmin.remote_user)==0):
    print '<p><b>%s: user "%s" is not a valid capisuite fax user<br> Your webmin user name must match a cs fax user (= *nix user) </b></p>' % (webmin.text['error'].upper(),webmin.remote_user)
else:
    print '<form action="newfax.cgi" method="POST"><input type="hidden" name="faxcreate" value="new"><input type=SUBMIT value="Newfax"></form>'
    print "<hr>\n<p><b> Send Queue</b></p>"
    capifaxwm.showfaxlist(webmin.remote_user)
    print "<p><b> Received List: Fax</b></p>"
    capifaxwm.showreceivedlist(webmin.remote_user,forwardopt=1,dldpage="download.cgi",removepage="abort.cgi")
    if capifaxwm.checkconfig("voice")!=-1:
	print "<p><b> Received List: Voice</b></p>"
	capifaxwm.showreceivedlist(webmin.remote_user,fileprefix="voice",dldpage="download.cgi",removepage="abort.cgi")
    
print "<p>&nbsp;</p><hr>"		
webmin.footer([("/", "index")])
#print "</body></html>"
