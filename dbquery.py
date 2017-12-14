# -*-coding: utf-8 -*-

try:
    import mysql.connector
except:
    import MySQLdb


class Row(dict):
    """A dict that allows for object-like property access syntax."""
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

class Gdbm(object):
    """通用数据库连接管理 general database mananger"""
    def __init__(self, host, user, passwd, db, charset="utf8"):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db
        try:
            self.conn = mysql.connector.connect(user=user, password=passwd, database=db, host=host, charset=charset)
            ## only work in version 2.0+
            # self.cursor = self.conn.cursor(dictionary=True)
            self.cursor = self.conn.cursor()
        except Exception as e:
            self.conn = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db,charset=charset)
            self.cursor = self.conn.cursor()#self.conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

    def query(self, sql, data=None):
        if data:
            self.cursor.execute(sql, data)
        else:
            self.cursor.execute(sql)
        data = self.cursor.fetchall()
        return [Row(d) if type(d) is dict else d for d in data]

    def execute(self, sql, data=None):
        if data:
            self.cursor.execute(sql, data)
        else:
            self.cursor.execute(sql)
        #pk = self.conn.insert_id() lastrowid
        self.conn.commit()
        #return pk

    def execute_no_commit(self, sql, data=None):
        """execute many sql then commit by hand"""
        if data:
            self.cursor.execute(sql, data)
        else:
            self.cursor.execute(sql)

    def query_as_dict(self, sql, data=None):
        """result is [dict{},...]"""
        if data:
            self.cursor.execute(sql, data)
        else:
            self.cursor.execute(sql)
        return dictfetchall(self.cursor)

    def get_desc(self):
        return [col[0] for col in self.cursor.description]

    def data_gen(self, sql, sql_count, PER_PAGE=1000):
        try:
            count = self.query(sql_count)[0][0]
        except Exception:
            raise StopIteration
        pages = lambda c, p:  c / p + 1 if c % p > 0 else c / p
        bs_pages = pages(count, PER_PAGE)

        i = 0
        while i < bs_pages:
            print '--page %s--'%i
            data = self.query_as_dict(sql+" limit %s, %s" %(i*PER_PAGE, PER_PAGE))
            if not data:
                raise StopIteration
            for d in data:
                yield d
            i += 1

    def data_gen_change(self, sql, sql_count, PER_PAGE=1000):
        try:
            count = self.query(sql_count)[0][0]
        except:
            raise StopIteration
        pages = lambda c, p:  c / p + 1 if c % p > 0 else c / p
        bs_pages = pages(count, PER_PAGE)

        i = 0
        while i < bs_pages:
            data = self.query_as_dict(sql+" limit %s" %(PER_PAGE))
            if not data:
                raise StopIteration
            for d in data:
                yield d
            i += 1

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.cursor.close()
        self.conn.close()

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        Row(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]


