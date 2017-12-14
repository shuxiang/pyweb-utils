#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
用途:
作者:shuxiang29
mail:shuxiang29@gmail.com
设计流程:
'''
__revision__ = "1.0.0.20130328"
__appname__  = "zthread"
__author__   = "zhaoqz"
__email__    = "zhaoqz+py@gmail.com"
__modules__  = ""

import sys
import time
import os.path

import traceback
import threading
from threading import Thread

from Queue import Queue
qw = Queue(0)
mq = {}
zmutex = threading.Lock()

def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target=f, args=args, kwargs=kwargs)
        thr.start()
    return wrapper

class ZWorker(threading.Thread):
    def __init__(self, method, args, runtype = 0):
        threading.Thread.__init__(self)
        self.method = method
        self.args =args
        self.runtype = runtype

    def run(self):

        if self.runtype == 0:# 直接执行方法
            self.method(self.args)
        elif self.runtype == 1: # 执行完队列任务后退出
            self.runQ()
        elif self.runtype == 2: # 执行完队列任务后等待
            self.runQD()
        elif self.runtype == 3: # 多类型队列
            self.runMQD()


    def runQ(self):

        while not qw.empty():
            try:
                data = zgetQ()
                if data is None:
                    time.sleep(0.01)
                    continue

                self.method(data, self.args)

            except:
                print "runQ exception"
                traceback.print_exc(file=sys.stdout)

    def runQD(self):

        while 1:
            try:
                data = zgetQ()

                if data is None:
                    time.sleep(0.01)
                    continue

                self.method(data, self.args)

            except:
                print "runQD exception"
                traceback.print_exc(file=sys.stdout)

    def runMQD(self):

        while 1:
            try:
                data = zgetMQ(self.args[0])

                if data is None:
                    time.sleep(0.01)
                    continue

                self.method(data, self.args)

            except:
                print "runMQD exception"
                traceback.print_exc(file=sys.stdout)


def zputQ(data):
    try:
        qw.put(data)
        return True
    except:
        traceback.print_exc()
        return False

def zgetQ():
    try:
        if qw.empty(): return None

        return qw.get_nowait()
    except:
        return None

    return None

def zputMQ(mtype, data):
    global zmutex
    zmutex.acquire()
    if mtype not in mq:
        mq[mtype] = Queue(0)

    zmutex.release()
    q= mq[mtype]
    q.put(data)

def zgetMQ(mtype):
    try:
        if mq[mtype].empty(): return None

        return mq[mtype].get_nowait()
    except:
        return None

    return None


def zStartThread(method, datas, block = True):
    """
    启动线程，执行线程方法
    """

    threads = []
    for data in datas:
        t = ZWorker(method, data, 0)
        t.setDaemon(True)
        t.start()
        threads.append((t))

    print "start thread."

    if block:
        for thread in threads:
            thread.join()

    return threads

def zStartThreadQ(method, datas, block = True):
    """
    启动线程，处理队列任务
    """

    threads = []
    for data in datas:
        t = ZWorker(method, data, 1)
        t.setDaemon(True)
        t.start()
        print "start thread", data
        threads.append((t))

    print "start [%d] thread." % len(datas)

    if block:
        for thread in threads:
            thread.join()

    return threads

def zStartThreadQD(method, datas, block = False):
    """
    启动线程，持续处理队列任务
    """

    threads = []
    for data in datas:
        t = ZWorker(method, data, 2)
        t.setDaemon(True)
        t.start()
        threads.append((t))

    print "start thread."

    if block:
        for thread in threads:
            thread.join()

    return threads


def zStartThreadMQD(method, datas, block = False):
    """
    启动线程，持续处理队列任务
    """

    threads = []
    for data in datas:
        t = ZWorker(method, data, 3)
        t.setDaemon(True)
        t.start()
        threads.append((t))

    print "start thread."

    if block:
        for thread in threads:
            thread.join()

    return threads

if __name__ == "__main__":

    datas = range(1,10)

    if 0:
        def print1(data):
            import time, random
            time.sleep(random.randint(1,10)/10)
            print "==>",data

        zStartThread(print1, datas)

    if 0:
        def printQ(data, args):
            print "a[%s_%s]" % (str(args), data)

        for i in range(100):
            zputQ("QQ%2d" % i)

        zStartThreadQ(printQ, datas)

    if 1:
        def printQD(data, args):
            print "a2[%s_%s]" % (str(args), data)

        for i in range(100):
            zputQ("QQ%2d" % i)

        zStartThreadQD(printQD, datas)

        for i in range(100):
            zputQ("MM%2d" % i)

