#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
用途:常用辅助处理功能
作者:shuxiang29
mail:shuxiang29@gmail.com
'''

import collections
import os
import traceback


def unicode2utf8(data):
    """
        转换输入对象为utf8格式
        @param data: 输入对象
        @return : 输出结果
    """
    if isinstance(data, unicode):
        return data.encode('utf8')
    if isinstance(data, str):
        return data
    elif isinstance(data, collections.Mapping):
        return dict(map(unicode2utf8, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(unicode2utf8, data))
    else:
        return data

def getXmlText(node, tag):
    """
        获取XML标签的内容
        @param node: XML节点
        @param tag: 目标XML标签
        @return : 返回内容
    """
    retvar = ''
    if node.find(tag) is not None:
        retvar =  node.find(tag).text
        if isinstance(retvar, unicode):
            retvar = retvar.encode('utf8')

    if retvar is None:
        retvar = ''
    return retvar.strip()

def trimHtmlTag(Str):
    """
        将HTML标签去空白，去换行符
        @param Str: 要处理的字符串
        @return :  返回过滤后的内容
    """
    outStr = ''
    inflag = 0
    for s in Str:
        if s == '<':
            inflag = 1
            continue
        if s == '>':
            inflag = 0
            continue
        if inflag == 1:
            continue
        outStr += s

    while outStr.find('  ') > 0:
        outStr = outStr.replace('  ', '')
    outStr = outStr.replace('\r', '')
    outStr = outStr.replace('\n', '')

    return outStr.strip()

def loadjson(jfile):
    """
        将json格式文件读取转换成json数据
        @param jfile: json格式数据文件
        @return : 返回json数据
    """
    import json
    if not os.path.exists(jfile) or not os.path.isfile(jfile):
        return {}
    jstr = open(jfile,'rt').read()
    if not jstr.strip().startswith('{') or not jstr.strip().endswith('}'):
        print "[%s] file is not a json file." % jfile
        return {}
    try:
        jcfg = json.loads(jstr)
        return unicode2utf8(jcfg)
    except:
        traceback.print_exc()
        return

def savejson(jcfg, jfile):
    """
        将json格式数据转换成字符串输出到文件
        @param jcfg: json格式数据
        @param jfile: 输出文件
    """
    import json
    try:
        jstr = json.dumps(jcfg, ensure_ascii=False, sort_keys=True, indent=2)
        open(jfile,'wt').write(jstr)
    except:
        traceback.print_exc()
        return


def getStrValue(Str, start, end):
    """
        字符串截取
        @param Str: 源字符串
        @param start: 起始位置
        @param end: 结束位置
        @return :  截取内容
    """
    s = Str.find(start)
    if s < 0:
        return ""
    e = Str[s + len(start):].find(end)
    if e < 0:
        return Str[s + len(start):].strip()
    return Str[s + len(start):][:e].strip()


def urldecode(querystr):
    import urllib
    d = {}
    if querystr.find('?') > 0:
        query = querystr.split('?', 1)[1]
    else:
        query = querystr

    if query.find('=') < 0:
        return d
    try:
        a = query.split('&')
        for s in a:
            if s.find('='):
                try:
                    k, v = map(urllib.unquote_plus, s.split('=', 1))
                    if k in d:
                        if isinstance(d[k], list): d[k].append(v)
                        else:d[k] = [d[k], v]
                    else:
                        d[k] = v
                except KeyError:
                    d[k] = v
    except:
        return d
    return d


def clean_text(txt):
    """
    清除异常字符
    """
    if txt is None:
        txt = ""
    if len(txt)>0:
        txt = txt.replace("\n", "").replace("\r", "").replace(" ","")
    return txt

if __name__ == "__main__":

    if 0:
        j = loadjson('1')
        print j
        j['1']=1
        savejson(j, '1')

    if 1:
        s = (u'3120002', u'PTR', u'2013-05-26', False, '2013-05-27 10:50:40')
        print unicode2utf8(s)

