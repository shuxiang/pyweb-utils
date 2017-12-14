#coding=utf8

import datetime
import smtplib
from email.mime.text import MIMEText
from email.header import Header

# mail config
mailconf = {'host':'smtp.mxhichina.com', 'user':'warning@haoshuchina.com', 'pass':'Hs123456', \
    'receivers':['703647752@qq.com']}#,'366499517@qq.com','21966758@qq.com']}

def send_mail(header, msg):
    msg = msg.encode('utf8') if type(msg) is unicode else msg
    message = MIMEText(msg, 'plain', 'utf-8')
    message['Subject'] = Header(header.encode('utf8'), 'utf-8')
    message['From'] = mailconf['user']
    message['To'] = ";".join(mailconf['receivers'])

    try:
        smtpObj = smtplib.SMTP(mailconf['host'])
        smtpObj.login(mailconf['user'], mailconf['pass'])
        smtpObj.sendmail(mailconf['user'], mailconf['receivers'], message.as_string())
    except smtplib.SMTPException, Exception:
        print u"--Error: 无法发送邮件"
    #print '--send mail:\n', msg