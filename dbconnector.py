#!/usr/bin/env python
# -*- coding: utf-8 -*-

import functools
import threading
import Queue
import dbhandler
import weakref
import traceback
import sys
import logging

RDB = 'rdb'
WDB = 'wdb'
MINLIMIT = 10
MAXLIMIT = 40


class ConnectionPoolOverLoadError(Exception):
    pass


class ConnectionNotInPoolError(Exception):
    pass


class ConnectionNameConflictError(Exception):
    pass


class AlreadyConnectedError(Exception):
    pass


class ClassAttrNameConflictError(Exception):
    pass


class ConnectionNotFoundError(Exception):
    pass


class ConnectionPool(object):

    def __init__(self, name, minlimit=MINLIMIT, maxlimit=MAXLIMIT, **kwargs):
        self.name = name
        self.minlimit = MINLIMIT
        self.maxlimit = MAXLIMIT
        self.kwargs = kwargs
        self.queue = Queue.Queue(self.maxlimit)
        self._lock = threading.Lock()
        self._live_connections = 0
        self._peak_connections = 0
        self._open_connections = []

    def __repr__(self):
        return "<%s of %s>" % (self.__class__.__name__, self.name)

    @property
    def live_connections(self):
        return self._live_connections

    def record_peak(self):
        with self._lock:
            if self._peak_connections < self._live_connections:
                self._peak_connections = self._live_connections

    def clearIdle(self):
        while self.queue.qsize() > self.minlimit:
            connect = self.queue.get()
            connect.close()
            del connect
            with self._lock:
                self._live_connections -= 1

    def connect(self):
        if self.queue.empty():
            self._connect()
            conn = self.queue.get()
        else:
            try:
                conn = self.queue.get()
                conn.ping()
            except:
                del conn
                conn = dbhandler.dblib.connect(**self.kwargs)
        self.record_open_connection(conn)
        return conn

    def record_open_connection(self, conn):
        with self._lock:
            self._open_connections.append(conn)

    def pop_open_connection(self, conn):
        with self._lock:
            try:
                self._open_connections.remove(conn)
            except Exception:
                raise ConnectionNotInPoolError("Connection seems not belong to %s" % self.__repr__())

    def _connect(self):
        """
        open the new connection ,
        :return:
        """
        with self._lock:
            if self.live_connections >= self.maxlimit:
                raise ConnectionPoolOverLoadError("Connections of %s reach limit!" % self.__repr__())
            else:
                self.queue.put(dbhandler.dblib.connect(**self.kwargs))
                self._live_connections += 1
        self.record_peak()

    def release(self, conn):
        self.pop_open_connection(conn)
        with self._lock:
            try:
                conn.rollback()
            except dbhandler.dblib.OperationalError:
                print "connection seems closed, drop it."
            else:
                self.queue.put(conn)
            finally:
                pass
                # self._live_connections -= 1
        self.clearIdle()


def get_class_attrs(cls):
    return [attr for attr in dir(cls) if not attr.startswith('_')]


class DataBaseConnector(object):

    _instance_lock = threading.Lock()
    _current = threading.local()
    _lock = threading.Lock()

    def __init__(self, connection_handler=None, delegate=False):
        """
        Global DataBaseConnector with specific connection handler,
        call DataBaseConnector.connect to passing the mysql connection to this handler
        and use DataBaseConnector.db access
        current database connection wrapper class.
        :param connection_handler:
        :return:
        """
        self._connection_handler = connection_handler
        self._connection_pools = {}
        # the queue stores available handler instance
        with DataBaseConnector._instance_lock:
            DataBaseConnector._instance = self
        self._current.conn = self._current.conn_name = self._current.handler = None
        self.set_delegate(delegate)

    def __getattr__(self, attr):
        if not self._delegate or (attr.startswith('_') or not hasattr(self._current,"handler")):
            return self.__getattribute__(attr)
        else:
            return getattr(self._current.handler, attr)

    def set_delegate(self, delegate):
        if delegate:
            if set(get_class_attrs(self._connection_handler)).intersection(set(get_class_attrs(self))):
                raise ClassAttrNameConflictError("If open delegate,ConnectionHandler's attr name should not appear in DataBaseConnector")
            self._delegate = True
        else:
            self._delegate = False

    def load_database_cfg(self):
        pass

    def add_database(self, database, minlimit=MINLIMIT, maxlimit=MAXLIMIT, **kwargs):
        """
        :param database: string database name
        :param kwargs: connection kwargs
        :return:
        """
        override = kwargs.pop("override", False)
        if not override and self._connection_pools.has_key(database):
            msg = "Alreay exist connection '%s',override or rename it." % database
            print msg
            # raise ConnectionNameConflictError(msg)
        else:
            self._connection_pools[database] = ConnectionPool(database, minlimit, maxlimit, **kwargs)

    def add_databases(self, **kwargs):
        """
        :param kwargs: use database name as key , connection kwargs dict as value
        :return:
        """

    def connect(self, conn_name, curstype='TUPLE', auto_commit=False):
        """
        Mapping current connection handler's method to DataBaseConnector
        :return:
        """
        if not hasattr(self._current, "handler") or self._current.handler is None:
            self._current.conn = self._connection_pools[conn_name].connect()
            self._current.conn_name = conn_name
            self._current.handler = self._connection_handler(conn_name, self._current.conn, curstype, auto_commit, db=self._connection_pools[conn_name].kwargs['db'])
            self._current.conn._cursor = weakref.proxy(self._current.handler._cursor)
        else:
            try:
                self._current.conn.ping()
                if dbhandler.dbtype == 1:
                    self._current.handler._cursor._connection = weakref.proxy(self._current.conn)
                else:
                    self._current.handler._cursor.connection = weakref.proxy(self._current.conn)
            except:
                self._current.conn = dbhandler.dblib.connect(**self._connection_pools[conn_name].kwargs)
                self._current.handler = self._connection_handler(conn_name, self._current.conn, curstype, auto_commit, db=self._connection_pools[conn_name].kwargs['db'])
            self._current.conn._cursor = weakref.proxy(self._current.handler._cursor)
            # raise AlreadyConnectedError("Database:'%s' is already connected !" % conn_name)

    def release(self):
        """
        :return:
        """
        conn = self._current.conn
        self._connection_pools[self._current.conn_name].release(conn)
        self._current.handler.close()
        del self._current.handler, self._current.conn

    @property
    def conn(self):
        return weakref.proxy(self._current.conn)

    @property
    def handler(self):
        return weakref.proxy(self._current.handler)

    @staticmethod
    def instance():
        if not hasattr(DataBaseConnector, "_instance"):
            with DataBaseConnector._instance_lock:
                if not hasattr(DataBaseConnector, "_instance"):
                    DataBaseConnector._instance = DataBaseConnector()
        return DataBaseConnector._instance


def with_db(dbname, curstype='TUPLE', auto_commit=False):

    """
    :param dbname:
    :return:the decorator with specific db connection
    """
    def _with_db(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            logger = logging.getLogger(__name__)
            logger.debug('.............with_db()')
            if not dbc._connection_pools.has_key(dbname):
                raise ConnectionNotFoundError("Not found connection for '%s', use dbc.add_database add the connection")
            dbc.connect(dbname, curstype, auto_commit)
            logger.debug('db connected!')
            try:
                res = func(*args, **kwargs)
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print ('Business error: %s' % ','.join(err_messages))
                res = None
            finally:
                dbc.release()
            return res
        return _wrapper
    return _with_db


dbc = DataBaseConnector(dbhandler.SimpleHandler, delegate=True)

@with_db(RDB, curstype='DICT')
def withMysqlQuery(sql, data=None, qt='all'):
    """
    :param conn_name:
    :return:the decorator with specific db connection
    """
    return dbc.handler.query(sql, data, qt)

@with_db(WDB, auto_commit=True)
def withMysqlInsert(sql, data=None, method='SINGLE'):
    """
    :param conn_name:
    :return:the decorator with specific db connection
    """
    return dbc.handler.insert(sql, data, method)

@with_db(WDB, auto_commit=True)
def withMysqlDelete(sql, data=None, method='SINGLE'):
    """
    :param conn_name:
    :return:the decorator with specific db connection
    """
    return dbc.handler.delete(sql, data, method)

@with_db(WDB, auto_commit=True)
def withMysqlUpdate(sql, data=None, method='SINGLE'):
    """
    :param conn_name:
    :return:the decorator with specific db connection
    """
    return dbc.handler.update(sql, data, method)

if __name__ == "__main__":

    dbc.add_database("db111", minlimit=3, maxlimit=10, host="58.83.130.111",
                    port=3306,
                    user="hoteltest",
                    passwd="hotel0807",
                    db="hotel20",
                    charset="utf8",
                    use_unicode = False)

    dbc.add_database("db172", minlimit=3, maxlimit=10, host="221.235.53.172",
                    port=3308,
                    user="histdata",
                    passwd="histdata0213",
                    db="histdata",
                    charset="utf8",
                    use_unicode = False)

    dbc.add_database("local", minlimit=3, maxlimit=10, host="127.0.0.1",
                    port=3306,
                    user="root",
                    passwd="",
                    db="innmall",
                    charset="utf8",
                    use_unicode = False)

    import time
    @with_db('local')
    def test2():
        print dbc.handler.show_tables()

    @with_db('local')
    def test3():
        print dbc.handler.show_tables()

    import threading
    threads = []
    for k in range(40):
        time.sleep(2)
        thread = threading.Thread(target=test2)
        threads.append(thread)
        thread.start()
    for k in range(40):
        time.sleep(3)
        thread = threading.Thread(target=test2)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    print "--------"




