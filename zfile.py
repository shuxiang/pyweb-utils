#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
用途:常用文件处理函数库
作者:shuxiang29
mail:shuxiang29@gmail.com
'''
__revision__ = "1.0.0.20121101"
__appname__  = "zfile"
__author__   = "shuxiang29"
__email__    = "shuxiang29@gmail.com"

import sys
import time
from ztime import *

FORMAT_DEFAULT    = "%Y-%m-%d %H:%M:%S"


def now(outformat=FORMAT_DEFAULT):
    return time.strftime(outformat,time.localtime())


def tail_f(file, filter = '', where = -1, endtime=''):
    """
        模拟linux tail -f 查看文件
        @param file: 文件
        @param filter: 查看特定目标
        @param where: 文件指针最后位置
        @param endtime: 结束时间
    """
    interval = 1.0
    if where == -1:
        where = file.tell()
    else:
        file.seek(where)

    while True:
        where = file.tell()
        line = file.readline()
        if not line:
            time.sleep(interval)
            file.seek(where)
        else:
            if filter == '' or  line.find(filter) > -1:
                yield (file.tell(),line)

        if endtime <> '' and now() > endtime:
            break

if __name__ == "__main__":

    if len(sys.argv) == 1:
        print "usage:%s file [keyword]" % sys.argv[0]
        sys.exit(0)

    tfile = sys.argv[1]

    if len(sys.argv) > 2:
        keyword = sys.argv[2]
    else:
        keyword = ''

    where = 3207
    for where, line in tail_f(open(tfile), keyword, where, getminute(1)):
        print where, line,
