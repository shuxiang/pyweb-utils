#!/usr/bin/env python
#coding: utf-8

import smtplib
import traceback

__author__ = 'shuxiang29'

import sys, smtplib, MimeWriter, base64, StringIO, os, string, time

from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def send_mail(send_from, send_to, subject, text, files=[],
              server="localhost", user = None, password = None, usessl = True):
    """
        发邮件
        @param send_from: 发邮件者
        @param send_to: 收邮件者
        @param subject: 邮件主题
        @param text: 内容
        @param files: 附件
        @param server: 发件地址
        @param user: 用户名
        @param password: 密码
        @param usessl: 是否使用HTTPS
    """
    assert type(send_to)==list
    assert type(files)==list

    msg = MIMEMultipart('alternative')
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text,'plain','utf-8') )

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    #smtp.set_debuglevel(1)
    if (user != None):
        smtp.ehlo()
        if usessl == True:
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, password)
        else:
            smtp_userid64 = base64.encodestring(user)
            smtp.docmd("auth", "login " + smtp_userid64[:-1])
            if password != None:
                smtp_pass64 = base64.encodestring(password)
                smtp.docmd(smtp_pass64[:-1])


    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

def send_html_mail(send_from, send_to, subject, text, html, files=[],
              server="localhost", user = None, password = None, usessl = True):
    """
        发带html格式邮件
        @param send_from: 发邮件者
        @param send_to: 收邮件者
        @param subject: 邮件主题
        @param text: 内容
        @param html: html内容
        @param files: 附件
        @param server: 发件地址
        @param user: 用户名
        @param password: 密码
        @param usessl: 是否使用HTTPS
    """
    assert type(send_to)==list
    assert type(files)==list

    msg = MIMEMultipart('alternative')
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    if text is not None and len(text) > 0:
        msg.attach( MIMEText(text,'plain','utf-8') )

    msg.attach( MIMEText(html, 'html', 'utf-8') )

    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(file))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    #smtp.set_debuglevel(1)
    if (user != None):
        smtp.ehlo()
        if usessl == True:
            smtp.starttls()
            smtp.ehlo()
            smtp.login(user, password)
        else:
            smtp_userid64 = base64.encodestring(user)
            smtp.docmd("auth", "login " + smtp_userid64[:-1])
            if password != None:
                smtp_pass64 = base64.encodestring(password)
                smtp.docmd(smtp_pass64[:-1])


    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

def easy_mail(send_to, subject, text):
    """
        快捷发邮件
        @param send_to: 收邮件者
        @param subject: 邮件主题
        @param text: 内容
    """
    try:
        send_mail('cron mail<13886127588@163.com>', send_to,
        subject, text, [], 'smtp.163.com', '13886127588', 'p13886127588')
    except:
        traceback.print_exc()

def easy_html_mail(send_to, subject, text, html):
    """
        快捷发带html格式邮件
        @param send_from: 发邮件者
        @param send_to: 收邮件者
        @param subject: 邮件主题
        @param text: 内容
        @param html: html内容
    """
    try:
        send_html_mail('cron mail<13886127588@163.com>', send_to,
        subject, text, html, [], 'smtp.163.com', '13886127588', 'p13886127588')
    except:
        traceback.print_exc()

if __name__ == "__main__":

    #easy_mail(['zhaoqz@innapp.cn'],'邮件测试标题', 'mail测试内容')
    html = """\
<html>
  <head></head>
  <body>
    <p>Hi!<br>
       How are you?<br>
       Here is the <a href="http://www.python.org">link</a> you wanted.
    </p>
<table cellspacing="0" cellpadding="1" border="1" width="400">
<tr>
<td width="100">你好</td>
<td width="300">他好</td>
</tr>
<tr>
<td width="100">你们好</td>
<td width="300">他们好</td>
</tr>
</table>

  </body>
</html>
"""

    html = """\
<table cellspacing="0" cellpadding="1" border="1" width="400">
<tr>
<td width="100">你好</td>
<td width="300">他好</td>
</tr>
<tr>
<td width="100">你们好</td>
<td width="300">他们好</td>
</tr>
</table>
"""
    easy_html_mail(['zhaoqz@innapp.cn'],'邮件测试标题', 'mail测试内容',html)

