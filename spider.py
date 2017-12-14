#!/usr/bin/python
# coding=utf-8
import weakref
import time
import datetime
import sys
import functools
from threading import Lock
from workflow import Workflows
import traceback

WORKNUM = 30
QUEUETYPE = 'P'
WORKTYPE = 'GEVENT'

class SpiderOrigin(Workflows):
    __lasttime = datetime.datetime.now()
    __lock = Lock()
    def __init__(self, worknum=WORKNUM, queuetype=QUEUETYPE, worktype=WORKTYPE, timeout=-1):
        super(SpiderOrigin, self).__init__(worknum=worknum, queuetype=queuetype, worktype=worktype)
        # Workflows.__init__(self, worknum=worknum, queuetype=queuetype, worktype=worktype)
        # Keeper.__init__(self)
        self.timeout = timeout
        self.prepare()
        self.dones = set()

    def prepare(self):
        pass

    def fetchDatas(self, flow, *args, **kwargs):
        """
            抓取酒店数据
            @param flow: 数据来源
            @param conditions: 条件限制
            @param terminal: 提前终结者
            @param filepath: 提前终结输出地方
            @return : 执行状态
        """
        try:
            self.extractFlow()
            start = time.time()
            self.fire(flow, *args, **kwargs)
            if self.timeout > -1:
                def check(self, timeout):
                    time.sleep(timeout)
                    self.exit()
                    print 'Time out of %s. ' % str(self.timeout)
                import threading
                wather = threading.Thread(target=check, args=(self, self.timeout - (time.time() - start)))
                wather.setDaemon(True)
                wather.start()
            self.waitComplete()
            self.dones.add(flow)
            end = time.time()
            self.totaltime = end - start
            return True
        except:
            traceback.print_exc()
            return False

    def clearDataOne(self, one):
        """
            清洗数据
            @param one: 待清洗的数据
            @return one: 返回清洗后的数据
        """
        pass

    def implementDataone(self, *args, **kwargs):
        """
             补充酒店数据
             @param *args: 元组参数
             @param **kwargs: 字典参数
        """
        pass

    @classmethod
    def uniquetime(cls, timespan=1, lasttime=None):
        if lasttime is None:
            with cls.__lock:
                cls.__lasttime = cls.__lasttime + datetime.timedelta(seconds=timespan)
                return cls.__lasttime
        else:
            cls.__lasttime = max(cls.__lasttime, lasttime)

    def statistic(self):
        for flow in self.dones:
            it = self.tinder(flow)
            print '==============Statistics of flow %s==============' % flow
            stat = {'total':{'succ':0, 'fail':0, 'timeout':0}} 
            total = {'succ':0, 'fail':0, 'timeout':0}
            stat[it.__name__] = {}
            stat[it.__name__]['succ'] = it.succ
            stat[it.__name__]['fail'] = it.fail
            stat[it.__name__]['timeout'] = it.timeout
            stat['total']['succ'] = stat['total']['succ'] + it.succ
            stat['total']['fail'] = stat['total']['fail'] + it.fail
            stat['total']['timeout'] = stat['total']['timeout'] + it.timeout
            print it.__name__, 'succ: ', it.succ
            print it.__name__, 'fail: ', it.fail
            print it.__name__, 'timeout: ', it.timeout
            while hasattr(it, 'next'):
                stat[it.next.__name__] = {}
                stat[it.next.__name__]['succ'] = it.next.succ
                stat[it.next.__name__]['fail'] = it.next.fail
                stat[it.next.__name__]['timeout'] = it.next.timeout
                stat['total']['succ'] = stat['total']['succ'] + it.next.succ
                stat['total']['fail'] = stat['total']['fail'] + it.next.fail
                stat['total']['timeout'] = stat['total']['timeout'] + it.next.timeout
                print it.next.__name__, 'succ: ', it.next.succ
                print it.next.__name__, 'fail: ', it.next.fail
                print it.next.__name__, 'timeout: ', it.next.timeout
                it = it.next
            print 'total succ: ', stat['total']['succ']
            print 'total fail: ', stat['total']['fail']
            print 'total timeout: ', stat['total']['timeout']
            print 'total time: ', self.totaltime

    def now(self):
        return datetime.datetime.now()

    def __del__(self):
        pass

if __name__ == '__main__':
    pass