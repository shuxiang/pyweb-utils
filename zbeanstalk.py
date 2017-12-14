#!/usr/bin/env python
# -*- coding:utf-8 -*-
'''
异步任务队列接口程序
参考文档：http://floss.zoomquiet.io/data/20110210135450/index.html
'''
import os

import sys
import json
import traceback
import time
import collections
import beanstalkc

class beanstalk:

    def __init__(self,host='localhost', port=11300, tubes = []):
        if isinstance(host, unicode):host = host.encode('utf8')
        if isinstance(port, unicode):port= port.encode('utf8')
        if isinstance(port, str):port= int(port)

        for i in range(3):
            try:
                self.bc=beanstalkc.Connection(host, port, connect_timeout = 10)
                if self.bc:
                    print "beanstalkc第[%d]连接[%s][%d]成功" % (i, host, port)
                    break
                print "beanstalkc第[%d]连接[%s][%d]失败，继续" % (i, host, port)
            except:
                traceback.print_exc()
                time.sleep(1)


        if self.bc and len(tubes) > 0:
            for tube in tubes:
                self.bc.watch(tube)

        return

    def __del__(self):
        self.bc.close()
        del self.bc

    def isOk(self):
        if not self.bc: return False
        return True

    def watch(self, tubes):
        if self.bc and len(tubes) > 0:
            for tube in tubes:
                self.bc.watch(tube)

    def get(self, tubes = [], timeout = 0):
        try:
            if len(tubes) > 0:
                self.bc.watch(tube)
            job=self.bc.reserve(timeout=timeout)
            if job is None:
                return None

        except:
            traceback.print_exc()
            return None

        return job

    def put(self, job, tube = "default", priority = 999, delay = 0, ttr = 30):

        try:
            self.bc.use(tube)
            if isinstance(job,basestring):
                self.bc.put(job,priority=priority,delay=delay,ttr=ttr)
            elif isinstance(job, collections.Container):
                task=json.dumps(job, ensure_ascii = False)
                self.bc.put(task,priority=priority,delay=delay,ttr=ttr)
            else:
                print "beanstalk只支持字符串格式job"
                return False
        except:
            traceback.print_exc()
            return False

        return True

    def getTubes(self):
        """
        :获取beanstalkd的管道类表
        """
        try:
            tubes = self.bc.tubes()
        except:
            print "getTubes exception ..."
            traceback.print_exc()
            return []

        return tubes


    def stats(self, tube = 'default'):

        """
        :获取管道状态
        """
        try:
            #判断该tube是否存在，不存在则说明没有任务，状态未空
            tubes=self.bc.tubes()
            if tube not in tubes:
                print "tube[%s]没有任务" % (tube)
                return True,{}

            stats = self.bc.stats_tube(tube)

            return True, stats

        except:
            traceback.print_exc()
            return False, {}

    def showStats(self, tube = 'default'):
        flag, stats = self.stats(tube)
        if not flag:
            print "无状态信息"
            return

        print json.dumps(stats, ensure_ascii=False, indent=4)


    def showAll(self, showtype = ''):
        tubes = self.getTubes()
        tubes.sort()
        print "-" * 60
        for tube in tubes:
            if showtype in ['ready']:
                flag, stats = bc.stats(tube)
                print "%-20s ready: %8d total: %8d" % (tube, stats.get('current-jobs-ready',0), stats.get('total-jobs',0))
            else:
                print "====>", tube, bc.showStats(tube)
        print "-" * 60
                


if __name__ == "__main__":

    usage = """Usage:
      zbeanstalk.py test <tube> [--host=<localhost>] [--port=<11300>]
      zbeanstalk.py clean <tube> [--host=<localhost>] [--port=<11300>]
      zbeanstalk.py showall [<type>] [--host=<localhost>] [--port=<11300>]
      zbeanstalk.py cleanall [--host=<localhost>] [--port=<11300>]

      Options:
          test    测试队列操作
          clean   清理队列
          showall 显示队列情况
          --host=<localhost>  服务器地址 [default: localhost].
          --port=<11300>  服务器端口 [default: 11300].
    """
    from docopt import docopt
    args = docopt(usage)
    print "args:",args
    host = args.get('--host')
    if not host: host='localhost'

    port= args.get('--port')
    if not port: port='11300'
    port = int(port)

    if args.get('test', False):
        tube = args.get('<tube>','default')

        bc = beanstalk(host=host, port=port)
        flag, stat = bc.stats(tube)
        print "启动，检查队列", bc.showStats(tube)

        bc.put('test job', tube)
        flag, stat = bc.stats(tube)

        print "放入1个任务，检查队列", bc.showStats(tube)

        bc.watch([tube])
        job = bc.get()
        print "job->", job.stats(), job.body


        flag, stat = bc.stats(tube)
        print "取出1个任务，检查队列", bc.showStats(tube)

        job.delete()

        flag, stat = bc.stats(tube)
        print "删除1个任务，检查队列", bc.showStats(tube)

        while 1:
            job = bc.get()
            if job:
                job.delete()
            else:
                break

        flag, stat = bc.stats(tube)
        print "删除全部任务，检查队列", bc.showStats(tube)

        del bc

    if args.get('clean', False):
        tube = args.get('<tube>','default')

        bc = beanstalk(host=host, port=port)
        flag, stat = bc.stats(tube)
        print "启动，检查队列", bc.showStats(tube)
        bc.watch([tube])

        while 1:
            job = bc.get()
            if job:
                job.delete()
            else:
                break

        flag, stat = bc.stats(tube)
        print "删除全部任务，检查队列", bc.showStats(tube)

        del bc

    if args.get('showall', False):
        bc = beanstalk(host=host, port=port)
        showtype = args.get('<type>','')
        bc.showAll(showtype)
        del bc

    if args.get('cleanall', False):
        bc = beanstalk(host=host, port=port)
        tubes = bc.getTubes()
        bc.watch(tubes)
        while 1:
            job = bc.get()
            if job:
                job.delete()
            else:
                break

