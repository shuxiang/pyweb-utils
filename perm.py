#!/usr/bin/env python
#coding=utf-8

"""
    perm.py
    ~~~~~~~~~~~~~
    
    permission extension
    :license: BSD
::

    from perm import *
    def valid(self):
        return g.user.get_roles
    Identity.valid = valid
    auth_perm = Permission([Role('auth'), Role('admin')])

    @auth_perm()
    def hello():
        return 'hello'
"""

__all__ = ['Role', 'Identity', 'Permission']

from functools import wraps

class Role(object):
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):
        return self.name == other.name
    def __str__(self):
        return self.name
    def __hash__(self):
        return hash(self.name)
        
class Identity(object):

    def __init__(self, permission, nexturl, exception):
        self.permission = permission
        self.exception = exception
        self.nexturl = nexturl

    def __call__(self, f):
        @wraps(f)
        def _decorated(*args, **kw):
            if self.permission.can(self.valid()):
                return f(*args, **kw)
            else:
                if self.exception:
                    if self.nexturl:
                        setattr(self.exception, 'nexturl', self.nexturl)
                    raise self.exception
                else:
                    e = Exception('You have not require role!')
                    if self.nexturl:
                        setattr(self.exception, 'nexturl', self.nexturl)
                    raise e
        return _decorated
        
    def valid(self):
        """you must rewrite this method then return a named Role instance"""
        pass
        
class Permission(object):
    def __init__(self, roles, exception=None):
        self.needs = set(roles)
        self.exception = exception

    def __call__(self, nexturl=None):
        return Identity(self, nexturl, self.exception)
        
    def can(self, roles):
        return len(set(roles) & self.needs) > 0

