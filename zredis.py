#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
对于redis的基础访问的一些封装
'''

import os,sys
import json
import logging

def redis_hset(redis, key, name, value):
    '''
    设置redis的hash键值, expire:-1为不超时;0为根据配置文件来统一;大于0表示按照用户设定的值来设置
    '''
    r = redis.hset(key, name, value)
    return r

def redis_hget(redis, key, name):
    '''读取redis的hash数据'''
    return redis.hget(key, name)

def redis_queue_qsize(redis, key):
    """Return the approximate size of the queue."""
    return redis.llen(key)

def redis_queue_empty(redis, key):
    """Return True if the queue is empty, False otherwise."""
    return redis_queue_qsize(redis, key) == 0

def redis_queue_put(redis, key, item):
    """Put item into the queue."""
    redis.rpush(key, item)

def redis_queue_get(redis, key, block=True, timeout=None):
    """Remove and return an item from the queue.

    If optional args block is true and timeout is None (the default), block
    if necessary until an item is available."""
    if block:
        item = redis.blpop(key, timeout=timeout)
    else:
        item = redis.lpop(key)
    if item:
        item = item[1]
    return item

def redis_expire(redis, key, expire):
    redis.expire(key, expire)
