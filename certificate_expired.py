#!/usr/bin/env python
# -*- coding: utf-8 -*-

from OpenSSL import SSL
import socket, datetime
import smtplib
from email.mime.text import MIMEText

alert_days = 30
port = 443
cert_tested = 0
cur_date = datetime.datetime.utcnow()
servers = open( "list.txt", "r")
response=""

def mail(response):
    from email.mime.text import MIMEText
    from subprocess import Popen, PIPE
    msg = MIMEText(response)
    msg["From"] = "123@123.com"
    msg["To"] = "456@456.com"
    msg["Subject"] = "Certificate expired warning !!"
    p = Popen(["/usr/sbin/sendmail", "-t", "-oi"], stdin=PIPE)
    p.communicate(msg.as_string())

for lists in servers:
    endpoint = lists.strip().split()[0]
    domain = lists.strip().split()[1]    
    cdn = lists.strip().split()[2]

    context = SSL.Context(SSL.SSLv23_METHOD)
    sock = SSL.Connection(context, socket.socket(socket.AF_INET, socket.SOCK_STREAM))

    try:
        sock.connect( (str(endpoint) , int(port)) )
        # Send empty to trigger response
        sock.send("\x00")
        get_peer_cert=sock.get_peer_certificate()
        sock.close()

        exp_date =  datetime.datetime.strptime(get_peer_cert.get_notAfter(),'%Y%m%d%H%M%SZ')
        days_to_expire = int((exp_date - cur_date).days)
        cert_tested = cert_tested + 1

        if alert_days > days_to_expire:
            response = response + "%s certificate %s will expires in %s days \n" % (cdn, domain, days_to_expire)
        # else:
        #     response = response + "%s certificate %s is OK \n" % (cdn, domain)

    except:
        response = "Unable to connect to %s : %s " % (endpoint, port)
        
# print response
if not response:
    continue
else:
    mail(response)
