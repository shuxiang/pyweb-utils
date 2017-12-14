#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
memcached访问连接池.
获取连接时候，先从连接池队列中获取，如果队列中没有可以使用的连接，则新创建。如果有连接，检查状态，如果无效，重新创建。如果有效，采用。
使用完毕后，归还给连接池队列中
"""
import os,sys
import traceback
import memcache
from ztime import now
import logging
from Queue import Queue

mmc_queue = Queue(0)

key_prefix = None

def get_key_prefix():
    """
    得到memcached的key前缀
    由于进程重启后，在memcached中保存的数据没有及时刷新，因此可能不利于及时切换版本，刷新数据。
    现在改成进程重启后，prefix会变化，导致key改变，因此原缓存的数据将立即作废。
    """
    global key_prefix
    if key_prefix is None:
        key_prefix = "__%s__" % (now()).replace(" ","").replace("-","").replace(":","")
        logging.debug("get_key_prefix() ==> new prefix created! %s" % key_prefix)
    return key_prefix


def get_mmcd_client(host, port, retry=3):
    global mmc_queue
    if host is None or port is None:
        logging.warn("get_mmcd_client failed, host[%s] port [%s]", host, port)
        return None

    mc = None
    if mmc_queue.qsize() > 0:
        mc = mmc_queue.get(block=False, timeout=1)
        logging.debug("after get_mmcd_client, queue size[%d], mc[%s]", mmc_queue.qsize(), mc)
    if mc is None:
        logging.debug('get_mmcd_client from Queue failed. New!')
        return new_mmcd_client(host, port, retry)
    else:
        stats = mc.get_stats()
        if not stats:
            print "memcached connection status is valid, delete and new!"
            mc.disconnect_all()
            del mc
            return new_mmcd_client(host, port, retry)
        else:
            logging.debug("get_mmcd_client success! mc[%s]", mc)
            return mc


def release_mmcd_client(mc):
    mmc_queue.put(mc)
    logging.debug("after release_mmcd_client, queue size[%d]", mmc_queue.qsize())


def new_mmcd_client(host, port, retry=3, debug=0):
    if host is None or port is None:
        return None

    print "new_mmcd_client ==> host[%s]port[%s]" % (host, port)
    mc = None
    i = 0
    while i < retry:
        try:
            addr = "%s:%s" % (host, port)
            mc = memcache.Client([addr], debug)

            stats = mc.get_stats()
            if not stats:
                print "memcached connect failed for [%d], retry again" % i
            else:
                logging.debug("memcached connect success! mc[%s]", mc)
                break
        except:
            traceback.print_exc()
            pass
        i += 1

    return mc

