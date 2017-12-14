#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
用途:常用时间处理函数
作者:shuxiang29
mail:shuxiang29@gmail.com
'''
__revision__ = "1.0.0.20120705"
__appname__  = "ztime"
__author__   = "zhaoqz"
__email__    = "zhaoqz+py@gmail.com"

import time,datetime
import calendar

FORMAT_DEFAULT    = "%Y-%m-%d %H:%M:%S"
FORMAT_ISO        = "%Y-%m-%dT%H:%M:%S.000+08:00"
FORMAT_DATE       = "%Y-%m-%d"
FORMAT_DATE_SHORT = '%Y%m%d'
FORMAT_TIME       = "%H:%M:%S"


def now(outformat=FORMAT_DEFAULT):
    """
        获取格式化后的当前时间的年月日 时分秒
        @param outformat: 格式
        @return : 格式化的时间串
    """
    return time.strftime(outformat,time.localtime())

def hour(outformat=FORMAT_TIME):
    """
        获取格式化后的当前时间的时分秒
        @param outformat: 格式
        @return : 格式化的时间串
    """
    return time.strftime(outformat, time.localtime())

def today(outformat = FORMAT_DATE):
    """
        获取格式化后的当前时间的年月日
        @param outformat: 格式
        @return : 格式化的时间串
    """
    return time.strftime(outformat,time.localtime())

def gethour(hours = 0, outformat = FORMAT_DEFAULT):
    """
        获取格式化后的当前时间以后某个时间点的年月日 时分秒
        @param hours: 间隔小时
        @param outformat: 格式
        @return : 格式化的时间串
    """
    lt   = time.strptime( now(), FORMAT_DEFAULT)
    lt_d = datetime.datetime(lt[0],lt[1],lt[2],lt[3],lt[4],lt[5])
    newtime= lt_d +datetime.timedelta(hours=hours)
    return newtime.strftime(outformat)

def getminute(mins = 0, outformat = FORMAT_DEFAULT):
    """
        获取格式化后的当前时间以后某个时间点的年月日 时分秒
        @param mins: 间隔分钟
        @param outformat: 格式
        @return : 格式化的时间串
    """
    lt   = time.strptime( now(), FORMAT_DEFAULT)
    lt_d = datetime.datetime(lt[0],lt[1],lt[2],lt[3],lt[4],lt[5])
    newtime= lt_d +datetime.timedelta(minutes=mins)
    return newtime.strftime(outformat)

def getdate(days = 0, outformat = FORMAT_DATE):
    """
        获取格式化后的当前时间以后某个时间点的年月日
        @param days: 间隔天数
        @param outformat: 格式
        @return : 格式化的时间串
    """
    lt   = time.strptime( now(), FORMAT_DEFAULT)
    lt_d = datetime.datetime(lt[0],lt[1],lt[2])
    newtime= lt_d +datetime.timedelta(days=days)
    return newtime.strftime(outformat)

def IsoDate2DateTime(isodate):
    """
        将标准格式的时间串的年月日 时分秒提取出来
        @param isodate: 时间字符串
        @return : 格式化的时间串
    """
    return isodate[:10]+' '+isodate[11:19]

def IsoDate2Date(isodate):
    """
        将标准格式的时间串的年月日提取出来
        @param isodate: 时间字符串
        @return : 格式化的时间串
    """
    return isodate[:10]

def wsdl2date(indate):
    """
        将带/连接的时间串变成-连接的时间串
        @param indate: 时间字符串
        @return : 格式化的时间串
    """
    l,r = indate.split()
    if l.find('/'):
        items = l.split('/')
    else:
        items = l.split('-')
    return "%4s-%02d-%02d" % (items[0],int(items[1]), int(items[2]))

def Date2IsoDate(date):
    """
        将时间串变成
        @param indate: 时间字符串
        @return : 格式化的时间串
    """
    return date +'T00:00:00.000+08:00'

def addDate(date, days, outformat = FORMAT_DATE):
    """
        获取格式化后的当前时间以后某个时间点的年月日
        @param days: 间隔天数
        @param outformat: 格式
        @return : 格式化的时间串
    """
    lt = date.split('-')
    lt_d = datetime.datetime(int(lt[0]),int(lt[1]),int(lt[2]))
    newtime= lt_d +datetime.timedelta(days=days)
    return newtime.strftime(outformat)

def date2short(date):
    """
        将年月日只取数字格式化成字符串
        @param date: 日期
        @return : 格式化的时间串
    """
    lt = date.split('-')
    return "%s-%d-%d" % (int(lt[0]), int(lt[1]), int(lt[2]))

#解析日期时间 2008-01-27 08:37:29
def getdatetime(s):
    """
        解析时间串为时间对象，或者日期串为日期对象
        @param s: 日期字符串
        @return : 时间
    """
    if len(s) >= 19:
        return datetime.datetime(*time.strptime(s[:19], '%Y-%m-%d %H:%M:%S')[:6])
    else:
        return datetime.datetime(*time.strptime(s[:10], '%Y-%m-%d')[:6])

def formatdatetime(s, outformat = FORMAT_DEFAULT):
    """
        将一种格式的时间串转换成另一种格式的时间串
        @param s: 日期字符串
        @param outformat: 格式
        @return : 格式化的时间串
    """
    dt = time.strptime(s,'%Y-%m-%d %H:%M:%S')
    return time.strftime(outformat,dt)

def date2second(s):
    """
        将日期字符串转换成秒数
        @param s: 日期
        @return : 格式化的时间串
    """
    if len(s) >=19:
        t = time.strptime(s[:19], '%Y-%m-%d %H:%M:%S')
    else:
        t = time.strptime(s[:10], '%Y-%m-%d')

    return time.mktime(t)

def gettimespan(stime, etime):
    """
        计算两个时间之间的间隔秒数
        @param stime: 起始时间字符串
        @param etime: 截止时间字符串
        @return : 秒数
    """
    if isinstance(etime, str):
        etime = getdatetime(etime)
    if isinstance(stime, str):
        stime = getdatetime(stime)

    delta = etime - stime
    return delta.seconds

def getdayspan(bdate, edate):
    """
        计算两个日期之间的天数
        @param stime: 起始日期字符串
        @param etime: 截止日期字符串
        @return : 天数
    """
    if isinstance(edate, basestring):
        edate = getdatetime(edate)
    if isinstance(bdate, basestring):
        sdate = getdatetime(bdate)

    delta = edate - sdate
    return delta.days

def getdateweek(dt):
    """
        返回星期数
        @param dt: 日期字符串
        @return : 第几个星期
    """
    y, m, d = dt.split('-')
    return datetime.date(int(y), int(m), int(d)).isoweekday()

#人性化的时间：2008-01-27 08:37:29
def friendly_time(stime, etime):
    """
        计算两个时间之间的间隔秒数
        @param stime: 起始时间字符串
        @param etime: 截止时间字符串
        @return : 返回间隔描述字符串
    """
    if isinstance(etime, str):
        etime = getdatetime(etime)
    if isinstance(stime, str):
        stime = getdatetime(stime)

    delta = etime - stime
    if delta.days >= 365:
        return '%d 年前' % (delta.days / 365)
    elif delta.days >= 30:
        return '%d 个月前' % (delta.days / 30)
    elif delta.days > 0:
        return '%d 天前' % delta.days
    elif delta.seconds < 60:
        return "%d 秒前!" % delta.seconds
    elif delta.seconds < 60 * 60:
        return "%d 分钟前" % (delta.seconds / 60)
    else:
        return "%d 小时前" % (delta.seconds / 60 / 60)

def getdates(sdate, days = 0):
    ''' 返回日期段 '''
    """
        得到起始日期到n天后的日期列表
        @param sdate: 起始日期字符串
        @param days: 天数
        @return : 返回日期列表
    """
    dates = []
    for i in range(days):
        dates.append(addDate(sdate, i))

    return dates

def getdates2(bdate, edate):
    '''
    返回bdate到edate之间的所有天
    '''
    dts = []
    dt = bdate
    while dt <= edate:
        dts.append(dt)
        dt = addDate(dt, 1)
    return dts

#时间戳（如1332888820），转化为日期时间字符串（如2012-03-28 06:53:40）
def timestamp_datetime(value):
    format = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(value)
    dt = time.strftime(format, value)
    return dt

#日期时间字符串（2012-03-28 06:53:40），转化为时间戳（如1332888820）
def datetime_timestamp(dt):
     time.strptime(dt, '%Y-%m-%d %H:%M:%S')
     s = time.mktime(time.strptime(dt, '%Y-%m-%d %H:%M:%S'))
     return int(s)

def dateFirstOfMonth(bdate):
    '''
    获取bdate所在月份的第一天
    '''
    return bdate[:8] + '01'

def dateEndOfMonth(bdate):
    '''
    获取bdate所在月份的最后一天
    '''
    lt = bdate.split('-')
    d = calendar.monthrange(int(lt[0]), int(lt[1]))[1]
    return bdate[:8] + '%02d' % d

def split_samemonth_days(bdate, edate):
    '''
    传递2个日期，按月进行划分，如果2个日期不在同一个月，产生从bdate到月底，月初到edate的多组日期
    例如，传入:(2014-12-12,2014-12-25)，返回:(2014-12-12,2014-12-25)
          传入:(2014-12-12,2015-01-25)，则返回:[(2014-12-12,2014-12-31),(2015-01-01,2015-01-25)]
    '''
    dates = []
    if bdate[:7] == edate[:7]:
        return [(bdate, edate)]
    while True:
        #获取bdate对应的该月最后1天
        dt2 = dateEndOfMonth(bdate)
        dates.append((bdate, dt2))
        bdate = addDate(dt2, 1) #下个月初
        if bdate[:7] == edate[:7]:
            dates.append((bdate, edate))
            break
    return dates


def add_seconds(stime, delta):
    '''
    获取某一个时间点(YYYY-MM-DD HH:mm:ss)，加上n秒后的时间
    '''
    t = datetime.datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')+datetime.timedelta(seconds=delta)
    return t.strftime('%Y-%m-%d %H:%M:%S')


def add_minutes(stime, delta):
    '''
    获取某一个时间点(YYYY-MM-DD HH:mm:ss)，加上n分钟后的时间
    '''
    t = datetime.datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')+datetime.timedelta(minutes=delta)
    return t.strftime('%Y-%m-%d %H:%M:%S')


def add_hours(stime, delta):
    '''
    获取某一个时间点(YYYY-MM-DD HH:mm:ss)，加上n小时后的时间
    '''
    t = datetime.datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')+datetime.timedelta(hours=delta)
    return t.strftime('%Y-%m-%d %H:%M:%S')


def add_days(stime, delta):
    '''
    获取某一个时间点(YYYY-MM-DD HH:mm:ss)，加上n小时后的时间
    '''
    t = datetime.datetime.strptime(stime,'%Y-%m-%d %H:%M:%S')+datetime.timedelta(days=delta)
    return t.strftime('%Y-%m-%d %H:%M:%S')

def add_months(stime, delta):
    '''
    获取某一个时间点(YYYY-MM-DD HH:mm:ss)，加上n个月后的时间
    '''
    if delta < 0:
        s = addDate(dateFirstOfMonth(stime), -1)
        return s[:8] + stime[8:]
    elif delta > 0:
        s = addDate(dateEndOfMonth(stime), 1)
        return s[:8] + stime[8:]


if __name__ == "__main__":

    print "now()=",now()
    print "hour()=",hour()
    print "today()=",today()
    print "today(FORMAT_DATE_SHORT)=",today(FORMAT_DATE_SHORT)
    print "gethour()=",gethour()
    print "gethour(-1, FORMAT_ISO)=",gethour(-1, FORMAT_ISO)
    print "gethour( 1, FORMAT_ISO)=",gethour( 1, FORMAT_ISO)
    print "getminute(-1, FORMAT_ISO)=",getminute(-1, FORMAT_ISO)
    print "getminute( 1, FORMAT_ISO)=",getminute( 1, FORMAT_ISO)

    print "getdate()=",getdate()
    print "getdate(-1)=",getdate(-1)
    print "getdate( 1)=",getdate( 1)
    print "addDate(%s, 1) = %s " % (getdate(), addDate(getdate(),1))
    print "addDate(%s, -1) = %s " % (getdate(), addDate(getdate(),-1))
    print "addDate(%s, 0, '%%m-%%d') = %s " % (getdate(), addDate(getdate(),0, '%m-%d'))
    print "date2short(%s)=%s" % (getdate(), date2short(getdate()))

    print "str2datetime(%s)-%s = %s" % (gethour(-25),now(), friendly_time(gethour(-25),now()))

    print "date2second('%s')=%s" % (getdate(), date2second(getdate()))
    print "date2second('%s')=%s" % (now(), date2second(now()))

    print "formatdatetime(%s)=%s" % ('2012-1-7 9:6:15',formatdatetime('2012-1-7 9:6:15'))

    print "getdayspan(%s, %s)=%d" % (getdate(-1), getdate(), getdayspan(getdate(-1), getdate()))

    print "getdates(%s, 5)=%s" % (getdate(), getdates(getdate(), 5))
    print "getdates(%s, 1)=%s" % (getdate(), getdates(getdate(), 1))

    print "timestamp_datetime(%d)=%s" % (1332888820, timestamp_datetime(1332888820))
    print "datetime_timestamp(%s)=%d" % ('2012-03-28 06:53:40', datetime_timestamp('2012-03-28 06:53:40'))

    print "getdates2('2014-12-12', '2015-01-05')=", getdates2('2014-12-12', '2015-01-05')
    print "dateFirstOfMonth('2012-12-16')=", dateFirstOfMonth('2012-12-16')
    print "dateEndOfMonth('2012-12-16')=", dateEndOfMonth('2012-12-16')
    print "split_samemonth_days('2014-12-16', '2014-12-20')=", split_samemonth_days('2014-12-16', '2014-12-20')
    print "split_samemonth_days('2014-11-16', '2015-01-20')=", split_samemonth_days('2014-11-16', '2015-01-20')
