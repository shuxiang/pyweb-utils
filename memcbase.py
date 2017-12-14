#!/usr/bin/env python
# -*- coding: utf-8 -*-

#memcached

import hashlib
import memcache


def hash(obj):
    m = hashlib.md5()
    m.update(obj)
    key = m.hexdigest()
    return key


def get_memclient(host, port, debug=0, retry=3):
    if host is None or port is None:
        return None

    mc = None
    i = 0
    while i < retry:
        try:
            addr = "%s:%s" % (host, port)
            mc = memcache.Client([addr], debug)

            stats = mc.get_stats()
            if not stats:
                print "memcache第[%d]次连接失败,重试" % i
            else:
                print "memcache连接成功"
                break
        except:
            print "get_memclient exception ..."
            pass
        i += 1

    return mc


