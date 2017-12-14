#!d:/python25/python.exe
# -*- coding: utf-8 -*-

import time, sys, string
import json
import logging
import os

try:
    import mysql.connector as dblib
    dbtype = 1
    class MySQLCursorDict(dblib.cursor.MySQLCursor):
        def _row_to_python(self, rowdata, desc=None):
            row = super(MySQLCursorDict, self)._row_to_python(rowdata, desc)
            if row:
                return dict(zip(self.column_names, row))
            return None
    #print "import mysql.connector"
except:
    #print "import mysql.connector failure! use MySQLdb"
    try:
        import MySQLdb   as dblib
        dbtype = 0
    except:
        raise "import MySQLdb and mysql.connector Error!"
    
class Mysql:
    """
        数据库封装
    """
    debug = 0
    charset = ''

    def __init__(self, db_host='localhost', db_user='', db_user_passwd='', db_name='', charset = '', debug = 0, db_port=3306, curstype='TUPLE'):
        """
            初始化数据库连接
            @param db_host: 地址
            @param db_user: 用户名
            @param db_user_passwd: 密码
            @param db_name: 数据库名称
            @param charset: 字符集
            @param debug: 调试模式
            @param db_port: 端口号
        """
        try:
            if isinstance(db_host, unicode):db_host = db_host.encode('utf8')
            if isinstance(db_user, unicode):db_user = db_user.encode('utf8')
            if isinstance(db_user_passwd, unicode):db_user_passwd = db_user_passwd.encode('utf8')
            if isinstance(db_name, unicode):db_name = db_name.encode('utf8')
            if isinstance(charset, unicode):charset= charset.encode('utf8')
            if isinstance(db_port, unicode):db_port= db_port.encode('utf8')
            if isinstance(db_port, str):db_port= int(db_port)

            if charset != '':
                self.mdb = dblib.connect(host=db_host, port=db_port, user=db_user, passwd=db_user_passwd, db=db_name, charset=charset, use_unicode = False ) #, charset='utf8'
                self.charset = charset
            else:
                self.mdb = dblib.connect(db_host, db_user, db_user_passwd, db_name, db_port )
            self.debug = debug
            #print "character_set_name:",self.mdb.character_set_name()
        except dblib.Error, error:
            print "Connect MySql[%s %s/%s %s] DB Error:"%(db_host,db_user,db_user_passwd,db_name),error,"\n"
            #sys.exit(1)
        else:
            if curstype == 'TUPLE':
                self.c = self.mdb.cursor()
            else:
                if dbtype:
                    self.c = self.mdb.cursor(cursor_class=MySQLCursorDict)
                else:
                    self.c = self.mdb.cursor(dblib.cursors.DictCursor)

            if self.charset != '':
                self.c.execute("SET NAMES '%s' " % self.charset)
                #print "character_set_name:",self.mdb.character_set_name()
                #self.c.set_character_set(self.charset)
        return

    def __del__(self):
        """
            关闭连接
        """
        self.c.close()
        self.mdb.close()
        del self.mdb
        return

    def rollback(self):
        self.c.execute("rollback")
        return

    def RenameTable(self,SrcTable,DesTable):
        """
            重命名表
            @param SrcTable: 表原名称
            @param DesTable: 表新名称
            @return : 返回操作状态
        """
        if len(SrcTable.strip())< 1 or len(DesTable.strip())< 1:
            return -1
        sql = "ALTER TABLE " + SrcTable + " RENAME " + DesTable + ";"
        try:
            self.c.execute(sql)
        except dblib.Error,error:
            print "RenameTable Error:",error
            return -1
        return 0

    def ExecSQL(self,SQL, params=None):
        """
            执行SQL语句
            @param SQL: SQL语句
            @param params: SQL语句的参数
            @return : 返回操作影响行数
        """
        sql = SQL
        if self.debug:
            print '[%d] %s' % (os.getpid(), sql)
        try:
            self.c.execute(sql,params)
        except dblib.IntegrityError,error:
            print sql
            print "ExecSQL IntegrityError",error
            return -2
        except dblib.Error,error:
            print sql
            print "ExecSQL Error:",error
            return -1
        return self.c.rowcount

    def MoveTable(self,SrcTable,DesTable):
        """
            移动表数据
            @param SrcTable: 源数据表
            @param DesTable: 目标数据表
            @return : 返回操作状态
        """
        sql = "INSERT INTO " + DesTable + " SELECT * FROM " + SrcTable + ";"
        if self.debug:    print sql
        try:
            self.c.execute(sql)
        except dblib.Error,error:
            print sql
            print "MoveTable Error:",error
            return -1
        return 0

    def TruncateTable(self,SrcTable):
        """
            清除表数据，自动ID复位
            @param SrcTable: 表名称
            @return : 返回操作状态
        """
        sql = "TRUNCATE TABLE "+ SrcTable + ";"
        if self.debug:    print sql
        try:
            self.c.execute(sql)
        except dblib.Error, error:
            print sql
            print "TruncateTable Error:", error
            return -1
        return 0

    def DropTable(self,Table):
        """
            删除表
            @param Table: 表名称
            @return : 返回操作状态
        """
        sql = "DROP TABLE "+ Table + ";"
        if self.debug:    print sql
        try:
            self.c.execute(sql)
        except dblib.Error, error:
            print sql
            print "DropTable Error:", error
            return -1
        return 0

    def TableExists(self,Table):
        """
            判断表是否存在
            @param Table: 表名称
            @return : 返回操作状态
        """
        sql = "SHOW TABLES LIKE '"+ Table + "';"
        if self.debug:    print sql
        Item = ""
        try:
            self.c.execute(sql)
        except dblib.Error,error:
            print "TableExists Error:",error
            return -1
        else:
            Data = self.c.fetchall()
            if len(Data) == 1:
                #print "Data:",Data
                Item = Data[0][0]
                #print "TableExists:%s" % Item
                if Item == Table:
                    return 1
        return 0

    def GetAColumn(self,sql, params=None):
        """
            获取一列数据
            @param sql: SQL语句
            @param params: SQL语句的参数
            @return Item: 返回一列数据
        """
        Item = ""
        if self.debug:
            print '[%d] %s' % (os.getpid(), sql)
        try:
            self.c.execute(sql,params)
        except dblib.Error,error:
            print sql
            print "GetACloumn Error:",error
            return Item
        else:
            Data = self.c.fetchall()
            if len(Data) == 1:
                Item = Data[0][0]
            else:
                if self.debug:  print "GetACloumn [%s] Error DataLen:" % sql, Data
        return Item

    def GetColumns(self,sql, params=None):
        """
            获取多列数据
            @param sql: SQL语句
            @param params: SQL语句的参数
            @return Item: 返回多列数据
        """
        Item = []
        if self.debug:    print sql
        try:
            self.c.execute(sql, params)
        except dblib.Error,error:
            print sql
            print "GetColumns Error:",error
            return Item
        else:
            Data = self.c.fetchall()
            if len(Data) == 1:
                Item = Data[0]

        return Item

    def GetSQLData(self,sql, params=None):
        """
            获取查询数据
            @param sql: SQL语句
            @param params: SQL语句的参数
            @return Data: 返回查询数据
        """
        Data = []
        if self.debug:
            print '[%d] %s' % (os.getpid(), sql)
        try:
            self.c.execute(sql, params)
        except dblib.Error,error:
            print sql
            print "GetSQLData Error:",error
            return Data
        else:
            Data = self.c.fetchall()

        return Data

    def GetSQLDataDict(self,sql, params=None):
        """
            获取查询数据，结果字典
            @param sql: SQL语句
            @param params: SQL语句的参数
            @return Dict: 返回查询数据字典
        """
        Dict = {}
        if self.debug:    print sql
        try:
            self.c.execute(sql, params)
        except dblib.Error,error:
            print sql
            print "GetSQLDataDict Error:",error
        else:
            Data = self.c.fetchall()
            for item in Data:
                Dict[item[0]] = tuple(item[1:])
                if self.debug: print "GetSQLDataDict:%s\t" % item[0],Dict[item[0]]
        return Dict

    def GetSQLDataDict2(self,sql, params=None):
        """
            获取查询数据，结果字典
            @param sql: SQL语句
            @param params: SQL语句的参数
            @return Dict: 返回查询数据字典
        """
        Dict = {}
        if self.debug:    print sql
        try:
            self.c.execute(sql, params)
        except dblib.Error,error:
            print sql
            print "GetSQLDataDict Error:",error
        else:
            Data = self.c.fetchall()
            for item in Data:
                if len(item) > 2:
                    if item[0] not in Dict:
                        Dict[item[0]] = {}
                    Dict[item[0]][item[1]] = tuple(item[2:])
                else:
                    Dict[item[0]] = tuple(item[1:])
        return Dict

    def GetTables(self):
        """
            查看数据库里面的数据表
            @return Item: 返回表信息
        """
        Items = []
        sql = "SHOW TABLES"
        try:
            self.c.execute(sql)
        except dblib.Error, error:
            print sql
            print "GetTables %s Error:" % sql, error
            return Items
        else:
            Data = self.c.fetchall()
            for item in Data:
                Items.append(item[0])
        return Items

    def GetTableFields(self, tablename):
        """
            查看数据表的列
            @param tablename: 表名称
            @return Items: 返回列信息
        """
        Items = []
        sql = "show full columns from %s" % tablename
        try:
            self.c.execute(sql)
        except dblib.Error, error:
            print sql
            print "GetTableFields %s Error:" % tablename, error
            return Items
        else:
            Items = self.c.fetchall()
        return Items

    def GetCreateTableSQL(self,Table,ToTable=""):
        """
            获取建表语句
            @param Table: 表名称
            @param ToTable: 建同样结构的表
            @return Item: 返回建表语句
        """
        Item = ""
        sql = "SHOW CREATE TABLE "+Table
        try:
            self.c.execute(sql)
        except dblib.Error,error:
            print sql
            print "GetCreateTableSql Error:",error
            return Item
        else:
            Data = self.c.fetchall()
            if len(Data) == 1:
                Item = Data[0][1]
        sql2 = Item.split("\n")
        if ToTable != "":
            sql2[0] = "CREATE TABLE "+ToTable+" ("
        Item = "\n".join(sql2)
        return Item

    def PrintDesc(self, Table):
        """
            格式化输出表结构信息
            @param Table: 表名称
        """
        fields = self.GetTableFields(Table)
        print "-" * 80
        print "%-20s %-15s %-8s %-10s %-20s" % ('name', 'type', 'is null', 'default', 'comment')
        print "-" * 80
        for field in fields:
            fname,ftype,fcollation,fnull,fkey,fdefault,fextra,fprivileges,fcomment = field
            print "%-20s %-15s %-8s %-10s %-20s" % (fname, ftype, fnull, fdefault, fcomment)
        print "-" * 80

    def Print (self, Data):
        """
            格式化输出
            @param Data: 输出内容
        """
        len_col = []
        printfmt = " "
        for item in Data:
            if len(len_col) < len(item):
                for i in range(len(item)):
                    len_col.append(0)
            for i in range(len(item)):
                if len_col[i] < len(str(item[i])):
                    len_col[i] = len(str(item[i]))

        print "","-"*80
        for lencol in len_col:
            printfmt += "%%%ds " % lencol

        for item in Data:
            print printfmt % item

        print "","-"*80

    def PrintData (self, SQL):
        """
            格式化输出查询结果
            @param SQL: SQL语句
        """
        Data = self.GetSQLData(SQL)
        self.Print(Data)

    def commit(self):
        """
            手动提交
        """
        self.mdb.commit()

    def GetInsertId(self):
        """
            @return :获取上次插入数据的ID
        """
        if dbtype == 1:
            return self.c.lastrowid
        else:
            return self.mdb.insert_id()

    def ShowTableInfo(self,Table):
        """
            打印表的信息
            @param Table:表名称
        """
        print "[%s]" % Table
        self.PrintDesc(Table)
        cnt = int(self.GetAColumn('select count(*) from ' + Table ) )
        if cnt > 0:
            #print "[%s Data]" % Table
            print "Count=%d" % cnt
            if cnt > 100:
               first = 50
            else:
               first = cnt
            self.PrintData('Select * from %s limit %d' % ( Table, first))

    def Sql2Strings(self, sql, split = '|', addtitle = False, forcealign = False):
        """
            导出sql返回的数据到文本列表中
            @param sql: SQL语句
            @param split: 间隔符
            @param addtitle: 添加名称
            @param forcealign: 是否处理换行符
            @return lines: 结果文本
        """

        lines = []
        datas = self.GetSQLData(sql)
        if addtitle:
            descs = self.c.description
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
                    #print type(d),d
                    l = len(str(d).decode('utf8').encode('gbk','ignore'))
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
                    line += ((fmt % str(d).decode('utf8').encode('gbk','ignore')).decode('gbk') + split).encode('utf8')
                line = line.replace('\r','\\r')
                line = line.replace('\n','\\n')
                lines.append(line)
            return lines

        else:
            for data in datas:
                line = ""
                for d in data:
                    if type(d) == type(u'1'):
                        d = d.encode('utf8')
                    line += str(d) + split
                line = line.replace('\r','\\r')
                line = line.replace('\n','\\n')
                lines.append(line)
            return lines

    def Sql2Table(self, sql, headers=[], addtitle = False, prefix='<table cellspacing="0" cellpadding="1" border="1">', postfix='</table>'):
        """
            导出sql返回的数据到html表格
            @param sql: SQL语句
            @param headers: 头信息
            @param addtitle: 添加名称
            @param prefix: 前缀
            @param postfix: 后缀
            @return html: 返回html内容，如下
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
            descs = self.c.description
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
            line = line.replace('\r','<br/>')
            line = line.replace('\n','<br/>')
            lines.append(line)
        html = prefix + string.join(lines,'\n') + postfix
        return html

    def Sql2File(self, sql, outfile, split= '|'):
        """
            导出数据到指定文件
            @param sql: SQL语句
            @param outfile: 输出文件
            @param split: 间隔符
            @return : 返回行数
        """

        lines = self.Sql2Strings(sql, split)
        fo = open(outfile,'at')
        for line in lines:
            fo.write(line+'\r\n')
        fo.close()

        return len(lines)


    def makecode(self, Table):
        fields = self.GetTableFields(Table)
        insert = 'insert into %s ({columns}) \n values ({values})' % Table
        update = 'update %s set {columns}' % Table
        columns = []
        ucolumns = []
        for field in fields:
            fname,ftype,fcollation,fnull,fkey,fdefault,fextra,fprivileges,fcomment = field
            columns.append(fname)
            ucolumns.append('%s = %%(%s)s' % (fname, fname))

        insert = insert.replace('{columns}', string.join(columns,',')).replace('{values}',"%(" + string.join(columns,')s,%(')+")s")
        print "-" * 80
        print insert
        update = update.replace('{columns}', string.join(ucolumns,','))
        print "-" * 80
        print update
        print "-" * 80
        for field in fields:
            fname,ftype,fcollation,fnull,fkey,fdefault,fextra,fprivileges,fcomment = field
            print 'print "%s=[%%s]" %% h["%s"]' % (fname, fname)


def dumptable(dbcfg, flag, tablename):
    """
        下载数据SQL语句
        @param flag: 是否写到文件
        @param tablename: 表名称
    """
    dbhost,dbuser,dbpass,dbname = dbcfg
    db = mysql(dbhost,dbuser,dbpass,dbname, debug = 0)

    tables = db.GetTables()
    sql = ''
    for tablename in tables:
        db.ShowTableInfo(tablename)
        if flag == 1:
            #db.ShowTableInfo(table)
            pass
        if flag == 2:
            sql += db.GetCreateTableSQL(tablename)+";\n\n"

    if flag == 2:
        open(dbname+".sql",'wt').write(sql)

def dumptabledata(dbcfg, tablename):
    """
        下载表数据SQL
        @param dbcfg: 数据库连接信息
        @param tablename: 表名称
    """
    dbhost,dbuser,dbpass,dbname = dbcfg
    db = mysql(dbhost,dbuser,dbpass,dbname, debug = 0)
    db.ShowTableInfo(tablename)

def makecode(dbcfg, tablename):
    ''' '''
    dbhost,dbuser,dbpass,dbname = dbcfg
    db = mysql(dbhost,dbuser,dbpass,dbname, debug = 0)
    db.makecode(tablename)

if __name__ == '__main__':

    mode = '-t'
    tablename = ''
    if len(sys.argv) < 5:
        print "Usage:\n      %s host user passwd dbname -[t.able list |d.ata  |s.ql |c.ode] [tablename]\n" % sys.argv[0]
        sys.exit()
    if len(sys.argv) >=5:
        dbhost   = sys.argv[1]
        dbuser   = sys.argv[2]
        dbpass = sys.argv[3]
        dbname = sys.argv[4]

    if len(sys.argv) >=6:
        mode = sys.argv[5]

    if len(sys.argv) >=7:
        tablename = sys.argv[6]


    if mode == '-t':
        dumptable((dbhost, dbuser, dbpass, dbname), 0, tablename)

    if mode == '-d':
        dumptable((dbhost, dbuser, dbpass, dbname), 1, tablename)

    if mode == '-s':
        dumptable((dbhost, dbuser, dbpass, dbname), 2, tablename)

    if mode == '-c':
        makecode((dbhost, dbuser, dbpass, dbname), tablename)
