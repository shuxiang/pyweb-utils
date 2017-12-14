#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import string

try:
    import mysql.connector as dblib

    dbtype = 1


    class MySQLCursorDict(dblib.cursor.MySQLCursor):
        def _row_to_python(self, rowdata, desc=None):
            row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
            if row:
                return dict(zip(self.column_names, row))
            return None
            # print "import mysql.connector"
except:
    # print "import mysql.connector failure! use MySQLdb"
    try:
        import MySQLdb as dblib

        dbtype = 0
    except:
        raise BaseException("import MySQLdb and mysql.connector Error!")


def fix_sql(sql, params):
    if sql == None:
        return sql

    if params != None and isinstance(params, dict) == True:
        sql = sql.replace(')s', ')')
        for k in params.keys():
            v = params.get(k, '')
            s1 = "%" + "(%s)" % (k)
            s2 = "'%s'" % (v)
            sql = sql.replace(s1, s2)
    sql = sql.replace('\n', ' ').replace('\t', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ').replace(
        '  ', ' ').replace('  ', ' ').replace('  ', ' ')
    return "[{}] - {}".format(os.getpid(), sql)


class BaseHandler(object):
    def __init__(self, conn_name, conn, curstype='TUPLE', auto_commit=False, db=''):
        self._name = conn_name
        self._conn = conn
        self._curstype = curstype
        if curstype == 'TUPLE':
            self._cursor = conn.cursor()
        else:
            if dbtype:
                self._cursor = conn.cursor(cursor_class=MySQLCursorDict)
            else:
                self._cursor = conn.cursor(dblib.cursors.DictCursor)
        if dbtype:
            self._conn.autocommit = auto_commit
        else:
            self._conn.autocommit(auto_commit)
        self.initialize()
        self.db = db

    def initialize(self):
        pass

    def show_tables(self):
        return '\n'.join([','.join(i) for i in self.fetch_data("show tables")])

    def close(self):
        """
        not close really , but relase connection
        :return:
        """
        self._cursor.close()
        del self._conn, self._cursor

    def queryAll(self, sql, data=None):
        """
            执行SQL
        """
        self._cursor.execute(sql, data)
        return self._cursor.fetchall()

    def queryOne(self, sql, data=None):
        """
            执行SQL
        """
        self._cursor.execute(sql, data)
        return self._cursor.fetchone()

    def query(self, sql, data=None, qt='all'):
        self._cursor.execute(sql, data)
        if qt.lower() == 'one':
            return self._cursor.fetchone()
        else:
            return self._cursor.fetchall()

    def operate(self, sql, data, method='SINGLE'):
        """
            操作数据
            @param sql:
            @param data: 数据
            @param method: 执行方式SINGLE, MANY
            @return : 影响行数
        """
        try:
            method = {'SINGLE': 'SINGLE', 'MANY': 'MANY'}[method]
        except:
            raise 'executing method error, you must choose SINGLE or MANY.'
        if method == 'SINGLE':
            num = self._cursor.execute(sql, data)
        else:  # MANY
            num = self._cursor.executemany(sql, data)
        return num

    def update(self, sql, data=None, method='SINGLE'):
        return self.operate(sql, data, method=method)

    def delete(self, sql, data=None, method='SINGLE'):
        return self.operate(sql, data, method=method)

    def insert(self, sql, data=None, method='SINGLE'):
        return self.operate(sql, data, method=method)

    def fetch_data(self, sql):
        self._cursor.execute(sql)
        return self._cursor.fetchall()


class SimpleHandler(BaseHandler):
    # debug = 1
    charset = 'utf8'

    def initialize(self):
        # self._cursor.execute("SET NAMES '%s' " % self.charset)
        self.debug = True

    def setDebug(self, debug):
        self.debug = debug

    def getDebug(self):
        return self.debug

    def RenameTable(self, SrcTable, DesTable):

        if len(SrcTable.strip()) < 1 or len(DesTable.strip()) < 1:
            return -1
        sql = "ALTER TABLE " + SrcTable + " RENAME " + DesTable + ";"
        try:
            self._cursor.execute(sql)
        except dblib.Error, error:
            print "RenameTable Error:", error
            return -1
        return 0

    def ExecSQL(self, SQL, params=None):

        sql = SQL
        if self.debug:
            print fix_sql(sql, params)
        try:
            self._cursor.execute(sql, params)
        except dblib.IntegrityError, error:
            print fix_sql(sql, params)
            print "ExecSQL IntegrityError", error
            return -2
        except dblib.Error, error:
            print fix_sql(sql, params)
            print "ExecSQL Error:", error
            return -1
        return self._cursor.rowcount


    def BatchExecSQL(self, SQLs, params=None, errstop=False):
        '''批量执行sql, 将每一条sql的执行结果加入到返回值列表中
           errstop表示如果执行出错, 是否直接返回
           如果errstop为True, 返回值列表的长度为执行了sql的条数, 否则返回值列表长度为所有sql
        '''
        rets = []
        for sql in SQLs:
            if self.debug:
                print 'sql count:', len(SQLs)
                print fix_sql(sql, params)
            try:
                self._cursor.execute(sql, params)
                r = self._cursor.rowcount
            except dblib.IntegrityError, error:
                print fix_sql(sql, params)
                print "ExecSQL IntegrityError", error
                r = -2
            except dblib.Error, error:
                print fix_sql(sql, params)
                print "ExecSQL Error:", error
                r = -1
            rets.append(r)
            if errstop and r<0:
                return rets
        return rets


    def MoveTable(self, SrcTable, DesTable):

        sql = "INSERT INTO " + DesTable + " SELECT * FROM " + SrcTable + ";"
        if self.debug:
            print sql
        try:
            self._cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "MoveTable Error:", error
            return -1
        return 0

    def TruncateTable(self, SrcTable):

        sql = "TRUNCATE TABLE " + SrcTable + ";"
        if self.debug:
            print sql
        try:
            self._cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "TruncateTable Error:", error
            return -1
        return 0

    def DropTable(self, Table):

        sql = "DROP TABLE " + Table + ";"
        if self.debug:
            print sql
        try:
            self._cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "DropTable Error:", error
            return -1
        return 0

    def TableExists(self, Table):

        sql = "SHOW TABLES LIKE '" + Table + "';"
        if self.debug:    print sql
        Item = ""
        try:
            self._cursor.execute(sql)
        except dblib.Error, error:
            print "TableExists Error:", error
            return -1
        else:
            Data = self._cursor.fetchall()
            if len(Data) == 1:
                # print "Data:",Data
                Item = Data[0][0]
                # print "TableExists:%s" % Item
                if Item == Table:
                    return 1
        return 0

    def GetAColumn(self, sql, params=None):

        Item = ""
        if self.debug:
            print fix_sql(sql, params)
        try:
            self._cursor.execute(sql, params)
        except dblib.Error, error:
            print fix_sql(sql, params)
            print "GetAColumn Error:", error
            return Item
        else:
            Data = self._cursor.fetchall()
            if len(Data) == 1:
                Item = Data[0][0]
            else:
                if self.debug:  print "GetAColumn [%s] Error DataLen:" % sql, Data
        return Item

    def GetColumns(self, sql, params=None):
        Item = []
        if self.debug:
            print fix_sql(sql, params)
        try:
            self._cursor.execute(sql, params)
        except dblib.Error, error:
            print sql
            print "GetColumns Error:", error
            return Item
        else:
            Data = self._cursor.fetchall()
            if len(Data) == 1:
                Item = Data[0]

        return Item

    def GetSQLData(self, sql, params=None):
        ''''''
        Data = []
        if self.debug:
            print fix_sql(sql, params)
        try:
            self._cursor.execute(sql, params)
        except dblib.Error, error:
            print fix_sql(sql, params)
            print "GetSQLData Error:", error
            return Data
        else:
            Data = self._cursor.fetchall()

        return Data

    def GetSQLDataDict(self, sql, params=None):
        ''''''
        Dict = {}
        if self.debug:
            print fix_sql(sql, params)
        try:
            self._cursor.execute(sql, params)
        except dblib.Error, error:
            print fix_sql(sql, params)
            print "GetSQLDataDict Error:", error
        else:
            Data = self._cursor.fetchall()
            for item in Data:
                Dict[item[0]] = tuple(item[1:])
                if self.debug: print "GetSQLDataDict:%s\t" % item[0], Dict[item[0]]
        return Dict

    def GetSQLDataDict2(self, sql, params=None):
        ''''''
        Dict = {}
        if self.debug:
            print fix_sql(sql, params)
        try:
            self._cursor.execute(sql, params)
        except dblib.Error, error:
            print fix_sql(sql, params)
            print "GetSQLDataDict Error:", error
        else:
            Data = self._cursor.fetchall()
            for item in Data:
                if len(item) > 2:
                    if item[0] not in Dict:
                        Dict[item[0]] = {}
                    Dict[item[0]][item[1]] = tuple(item[2:])
                else:
                    Dict[item[0]] = tuple(item[1:])
        return Dict

    def GetTables(self):

        Items = []
        sql = "SHOW TABLES"
        try:
            self._cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "GetTables %s Error:" % sql, error
            return Items
        else:
            Data = self._cursor.fetchall()
            for item in Data:
                Items.append(item[0])
        return Items

    def GetTableFields(self, tablename):

        Items = []
        sql = "show full columns from %s" % tablename
        try:
            self._cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "GetTableFields %s Error:" % tablename, error
            return Items
        else:
            Items = self._cursor.fetchall()
        return Items

    def showColumns(self, table):
        """
            查看表的列
            @param table: 表名称
            @return columns: 列名
        """
        sql = """ select `column_name`, `data_type`
                    from information_schema.columns
                where `table_schema` = %s and `table_name`=%s
        """
        columns = {}
        tables = self.queryAll(sql, (self.db, table))
        usetype = \
        {'DICT': {'column_name': 'column_name', 'data_type': 'data_type'}, 'TUPLE': {'column_name': 0, 'data_type': 1}}[
            self._curstype]
        for col in tables:
            colname = str(col[usetype['column_name']])
            coltype = str(col[usetype['data_type']])
            if 'int' in coltype.lower():
                columns[colname] = int
            elif 'double' in coltype or 'float' in coltype:
                columns[colname] = float
            else:
                columns[colname] = str
        return columns

    def GetCreateTableSQL(self, Table, ToTable=""):

        Item = ""
        sql = "SHOW CREATE TABLE " + Table
        try:
            self._cursor.execute(sql)
        except dblib.Error, error:
            print sql
            print "GetCreateTableSql Error:", error
            return Item
        else:
            Data = self._cursor.fetchall()
            if len(Data) == 1:
                Item = Data[0][1]
        sql2 = Item.split("\n")
        if ToTable != "":
            sql2[0] = "CREATE TABLE " + ToTable + " ("
        Item = "\n".join(sql2)
        return Item

    def PrintDesc(self, Table):
        fields = self.GetTableFields(Table)
        print "-" * 80
        print "%-20s %-15s %-8s %-10s %-20s" % ('name', 'type', 'is null', 'default', 'comment')
        print "-" * 80
        for field in fields:
            fname, ftype, fcollation, fnull, fkey, fdefault, fextra, fprivileges, fcomment = field
            print "%-20s %-15s %-8s %-10s %-20s" % (fname, ftype, fnull, fdefault, fcomment)
        print "-" * 80

    def Print(self, Data):

        len_col = []
        printfmt = " "
        for item in Data:
            if len(len_col) < len(item):
                for i in range(len(item)):
                    len_col.append(0)
            for i in range(len(item)):
                if len_col[i] < len(str(item[i])):
                    len_col[i] = len(str(item[i]))

        print "", "-" * 80
        for lencol in len_col:
            printfmt += "%%%ds " % lencol

        for item in Data:
            print printfmt % item

        print "", "-" * 80

    def PrintData(self, SQL):

        Data = self.GetSQLData(SQL)
        self.Print(Data)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def GetInsertId(self):
        if dbtype == 1:
            return self._cursor.lastrowid
        else:
            return self._conn.insert_id()

    def ShowTableInfo(self, Table):
        print "[%s]" % Table
        self.PrintDesc(Table)
        cnt = int(self.GetAColumn('select count(*) from ' + Table))
        if cnt > 0:
            # print "[%s Data]" % Table
            print "Count=%d" % cnt
            if cnt > 100:
                first = 50
            else:
                first = cnt
            self.PrintData('Select * from %s limit %d' % (Table, first))

    def Sql2Strings(self, sql, split='|', addtitle=False, forcealign=False):
        """
        导出sql返回的数据到文本列表中
        """

        lines = []
        datas = self.GetSQLData(sql)
        if addtitle:
            descs = self._cursor.description
            line = ""
            for desc in descs:
                line += str(desc[0]) + split
            lines.append(line)
            print line

        if forcealign:
            alignlens = {}
            for data in datas:
                i = 0
                for d in data:
                    i += 1
                    if type(d) == type(u'1'):
                        d = d.encode('utf8')
                    # print type(d),d
                    l = len(str(d).decode('utf8').encode('gbk', 'ignore'))
                    if i not in alignlens:
                        alignlens[i] = l
                    else:
                        if l > alignlens[i]:
                            alignlens[i] = l

            for data in datas:
                line = ""
                i = 0
                for d in data:
                    i += 1
                    if type(d) == type(u'1'):
                        d = d.encode('utf8')
                    fmt = "%%-%ds" % alignlens[i]
                    line += ((fmt % str(d).decode('utf8').encode('gbk', 'ignore')).decode('gbk') + split).encode('utf8')
                line = line.replace('\r', '\\r')
                line = line.replace('\n', '\\n')
                lines.append(line)
            return lines

        else:
            for data in datas:
                line = ""
                for d in data:
                    if type(d) == type(u'1'):
                        d = d.encode('utf8')
                    line += str(d) + split
                line = line.replace('\r', '\\r')
                line = line.replace('\n', '\\n')
                lines.append(line)
            return lines

    def Sql2Table(self, sql, headers=[], addtitle=False, prefix='<table cellspacing="0" cellpadding="1" border="1">',
                  postfix='</table>'):
        """
        导出sql返回的数据到html表格
        <tr>
        <td width="100">你好</td>
        <td width="300">他好</td>
        </tr>
        <tr>
        <td width="100">你们好</td>
        <td width="300">他们好</td>
        </table>
        """

        lines = []
        datas = self.GetSQLData(sql)

        if len(datas) < 1:
            return ''

        if len(headers) > 0:
            line = "<tr>"
            for header in headers:
                line += "<td>%s</td>" % str(header)
            line += "</tr>"
            print line
            lines.append(line)

        if addtitle:
            descs = self._cursor.description
            line = "<tr>"
            for desc in descs:
                line += "<td>%s</td>" % str(desc[0])
            line += "</tr>"
            lines.append(line)
            print line

        for data in datas:
            line = "<tr>"
            for d in data:
                if type(d) == type(u'1'):
                    d = d.encode('utf8')
                line += "<td>%s</td>" % str(d)
            line += "</tr>"
            line = line.replace('\r', '<br/>')
            line = line.replace('\n', '<br/>')
            lines.append(line)
        html = prefix + string.join(lines, '\n') + postfix
        return html

    def Sql2File(self, sql, outfile, split='|'):
        """
        导出数据到指定文件
        """

        lines = self.Sql2Strings(sql, split)
        fo = open(outfile, 'at')
        for line in lines:
            fo.write(line + '\r\n')
        fo.close()

        return len(lines)

    def makecode(self, Table):
        fields = self.GetTableFields(Table)
        insert = 'insert into %s ({columns}) \n values ({values})' % Table
        update = 'update %s set {columns}' % Table
        columns = []
        ucolumns = []
        for field in fields:
            fname, ftype, fcollation, fnull, fkey, fdefault, fextra, fprivileges, fcomment = field
            columns.append(fname)
            ucolumns.append('%s = %%(%s)s' % (fname, fname))

        insert = insert.replace('{columns}', string.join(columns, ',')).replace('{values}', "%(" + string.join(columns,
                                                                                                               ')s,%(') + ")s")
        print "-" * 80
        print insert
        update = update.replace('{columns}', string.join(ucolumns, ','))
        print "-" * 80
        print update
        print "-" * 80
        for field in fields:
            fname, ftype, fcollation, fnull, fkey, fdefault, fextra, fprivileges, fcomment = field
            print 'print "%s=[%%s]" %% h["%s"]' % (fname, fname)
