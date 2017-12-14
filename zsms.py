#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
用途:发送短信接口
作者:shuxiang29
mail:shuxiang29@gmail.com
设计流程:
'''
__revision__ = "1.0.0.20120517"
__appname__  = "sms"
__author__   = "shuxiang29"
__email__    = "shuxiang29@gmail.com"
__modules__  = "requests"

import sys
import time
import os.path
import traceback
import requests

#常用变量
def now():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    
pwd = os.path.abspath(os.path.dirname(__file__)) + "\\"

def show_version ():
    print "\n%s %s by %s" % (__appname__, __revision__, __author__)
    print "Email: %s" % (__email__)
    print "Powerd by PYTHON！(python 2.7 %s)\n" % __modules__

def show_help ():
    __args__     = "mobile|file content [token]"
    print "命令用法:\n    [-u|-f] %s %s \n" % (os.path.basename(sys.argv[0]), __args__) 
    print "参数说明:"
    print "    -u,-U: 单用户发送"
    print "    -f,-F: 按照文件群发"
    print "    -h,-H: 显示本帮助"
    return

def makePost(mobile, content, token = "7100518830323341"):

    post = {
    "mobile":mobile,
    "FormatID":"8",
    "Content":content,
    "ScheduleDate":now()[:10],
    "TokenID":token
    }
    return post

def SendSMS(phone, contents, token="7100518830323341"):
    '''
    发送短信API
    <?xml version="1.0" encoding="utf-8"?>
    <string xmlns="http://mms.wemediacn.com/">OK:[201207173372007671005188]</string>
    '''

    url = "http://h.133.cn:7992/webservice/smsservice.asmx/SendSMS"
    print url,
    data = makePost(phone, contents, token)
    print data

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    try:
        r = requests.post(url, data, headers = headers, allow_redirects=False)
        code = r.status_code
        contents = r.text
    except:
        code = 0
        contents = ''
        traceback.print_exc(file=sys.stdout)

    print code,url

    if code <> 200:
        return False

    if contents.find('>OK:[') < 0:
        #print contents.split('ERROR:')[1].split(']')[0]+"]"
        return False

    msgid = contents.split('>OK:[')[1].split(']')[0]
    print 'msgid=',msgid
    return True



def SendFile(pushfile, contents):

    i = 0
    try:
        fo = open(pushfile+'.result','wt')
        lines = open(pushfile,'rt').readlines()
        for line in lines:
            phone = line.strip().split(',')[0]
            if len(phone) != 11:
                fo.write('phone error[%s]\n', phone)
                continue
            i += 1
            flag = SendSMS(phone, contents)
            if flag:
                fo.write('%5d SendSms[%s] [%s] [ok]\n' % (i, phone, contents))
            else:
                fo.write('%5d SendSms[%s] [%s] [err]\n' % (i, phone, contents))
            if i==1:
                raw_input('please check sms contents, and press any key to continue')
            fo.flush()

        fo.close()
    except:
        traceback.print_ext()
        print "except:",i


if __name__ == "__main__":

    show_version()
    if len(sys.argv) < 4:
        show_help()
        sys.exit()
    try:
 
        if  sys.argv[1] in ['-u','-U']:
            phone = sys.argv[2]
            contents = sys.argv[3]
            if len(sys.argv) > 4:
                 token = sys.argv[4]
                 print SendSMS(phone, contents, token)
            else:
                 print SendSMS(phone, contents)
        elif sys.argv[1] in ['-f','-F']:
            pushfile = sys.argv[2]
            contents = sys.argv[3]
            print SendFile(pushfile, contents)
    except:
        print "运行异常:"
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        
