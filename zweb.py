#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
用途:常用网页抓取函数
作者:shuxiang29
mail:shuxiang29@gmail.com
'''

import collections
import os
import traceback
import requests
from zmisc import unicode2utf8, getStrValue

def getUrl(url, timeout = 30):
    """
        使用HTTPget方法获取网页内容
        @param url: 地址
        @param timeout: 超时时间
        @return content: 返回抓取内容
    """
    try:
        r = requests.get(url, timeout = timeout)
        print url, r.status_code
        if r.status_code <> 200:
            return ""

        content = r.content

        #:text/html; charset=gbk
        content_type = r.headers.get('content-type','')
        if content_type.find('charset') >  -1:
            charset = content_type.split('charset=')[1].split()[0]
            if charset in ['gbk','gb2312']:
                content = content.decode(charset).encode('utf8')
        else:
            content = unicode2utf8(r.content)
        return content

    except:
        traceback.print_exc()

    return ''

def getUrlStr(url, bstr, estr, timeout = 30):
    """
        提取网页的部分内容
        @param url: 地址
        @param bstr: 起始字符串
        @param estr: 截止字符串
        @param timeout: 超时时间
        @return :提取结果
    """
    content = getUrl(url, timeout)
    if len(content) < 1:
        return ''
    return getStrValue(content, bstr, estr)


def getUrlStrs(url, keyinfos, timeout = 30):
    """
        提取网页的多个部分内容
        @param url: 地址
        @param keyinfos: 起始字符串、截止字符串的列表
        @param timeout: 超时时间
        @return :提取结果
    """
    content = getUrl(url, timeout)
    if len(content) < 1:
        return {}
    ret = {}
    for key in keyinfos:
        ret[key] = getStrValue(content, keyinfos[key][0], keyinfos[key][1])

    return ret


if __name__ == "__main__":


    if 0:
        keyinfos = {'hid':["var city='","'"],'mapinfo':['var mapData=',';'] }
        url = 'http://www.118inns.com/index.php/booking/show/hid/93.html'
        ret = getUrlStrs(url, keyinfos)
        print ret

        url = 'http://www.jyinns.com/index.php?m=content&c=index&a=show&catid=7&id=106'
        print getUrlStr(url,'name = "','";')


    print getUrlStr("http://www.998.com/Reservations/Hotel010003.html","酒店电话：","&nbsp;")