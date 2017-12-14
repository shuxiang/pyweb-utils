#!/usr/bin/python
# coding=utf-8
__revision__ = "2015.03.03"
__appname__  = "innmall"
__author__   = "shuxiang29"
__email__    = "shuxiang29@gmail.com"

"""
   追踪工具（日志）和print工具
"""
import sys
import os
import datetime
import logging
import traceback
from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

LOGDEBUG = True
LOGDIR = '/tmp/log/'
FILEDIR = '/tmp/file/'
TIMEOUT = 10

def modulepath(filename):
    """
    Find the relative path to its module of a python file if existing.

    filename
      string, name of a python file
    """
    filepath = os.path.abspath(filename)
    prepath = filepath[:filepath.rindex('/')]
    postpath = '/'
    if prepath.count('/') == 0 or not os.path.exists(prepath + '/__init__.py'):
        flag = False
    else:
        flag = True
    while True:
        if prepath.endswith('/lib') or prepath.endswith('/bin') or prepath.endswith('/site-packages'):
            break
        elif flag and (prepath.count('/') == 0 or not os.path.exists(prepath + '/__init__.py')):
            break
        else:
            for f in os.listdir(prepath):
                if '.py' in f:
                    break
            else:
                break
            postpath = prepath[prepath.rindex('/'):].split('-')[0].split('_')[0] + postpath
            prepath = prepath[:prepath.rindex('/')]
    return postpath.lstrip('/') + filename.split('/')[-1].replace('.pyc', '').replace('.py', '') + '/'

def modulename(filename):
    """
    Find the modulename from filename.

    filename
      string, name of a python file
    """
    return filename.split('/')[-1].replace('.pyc', '').replace('.py', '')

def _cs(obj, encoding='utf8'):
    """
        将对象转换成字符串
        @param obj: 输入对象
        @param return: 输出字符串
    """
    if isinstance(obj, unicode):
        return obj.encode(encoding)
    elif isinstance(obj, str):
        return obj
    else:
        return str(obj)

def _cu(string, encoding='utf8'):
    """
        将对象转换成字符串
        @param obj: 输入字符串
        @param return: 输出对象
    """
    if isinstance(string, unicode):
        return string
    elif isinstance(string, str):
        try:
            return string.decode(encoding)
        except:
            import chardet
            det = chardet.detect(string)
            if det['encoding']:
                return string.decode(det['encoding'], 'ignore')
            else:
                return string.decode('gbk', 'ignore')
    else:
        return unicode(string)

def _print(*args):
    """
        打印gbk字符串
        @param *args: 打印内容
    """
    if not LOGDEBUG:
        return
    if not args:
        return
    encoding = 'gbk'
    args = [_cs(a, encoding) for a in args]
    f_back = None
    try:
        raise Exception
    except:
        f_back = sys.exc_traceback.tb_frame.f_back
    f_name = f_back.f_code.co_name
    filename = os.path.basename(f_back.f_code.co_filename)
    m_name = os.path.splitext(filename)[0]
    prefix = ('[%s.%s]'%(m_name, f_name)).ljust(20, ' ')
    if os.name == 'nt':
        for i in range(len(args)):
            v = args [i]
            if isinstance(v, str):
                args[i] = v #v.decode('utf8').encode('gbk')
            elif isinstance(v, unicode):
                args[i] = v.encode('gbk')
    print '[%s]'%str(datetime.datetime.now()), prefix, ' '.join(args)

def _print_err(*args):
    """
        打印错误内容，突出显示
        @param *args: 打印内容
    """
    if not LOGDEBUG:
        return
    if not args:
        return
    encoding = 'utf8' if os.name == 'posix' else 'gbk'
    args = [_cs(a, encoding) for a in args]
    f_back = None
    try:
        raise Exception
    except:
        f_back = sys.exc_traceback.tb_frame.f_back
    f_name = f_back.f_code.co_name
    filename = os.path.basename(f_back.f_code.co_filename)
    m_name = os.path.splitext(filename)[0]
    prefix = ('[%s.%s]'%(m_name, f_name)).ljust(20, ' ')
    print bcolors.FAIL+'[%s]'%str(datetime.datetime.now()), prefix, ' '.join(args) + bcolors.ENDC


def logprint(logname, category, level='INFO', maxBytes=1024*10124*100,
             backupCount=15, to_stdout=True, sentrykey=''):
    """
        生成日志输出的方法和对象
        @param logname 日志名称
        @param category 日志路径
        @param level 日志输出级别 (可选)
        @param maxBytes 日志单次输出最大长度 (可选)
        @param backupCount 日志轮询备份记录 (可选)
        @param to_stdout 是否屏幕输出 (可选)
        @param sentrykey 输送到sentry的配置 (可选)
        @return _wraper 返回日志方法
        @return logger 返回日志对象
    """
    path = os.path.join(LOGDIR, category, logname + '.log')
    print "log path:", path
    if not os.path.exists(path[:path.rindex('/')]):
        os.makedirs(path[:path.rindex('/')])

    # Initialize logger
    logger = logging.getLogger(logname)
    # frt = logging.Formatter('%(message)s')
    frt = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    hdr = None
    if path:
        # hdr = RotatingFileHandler(path, 'a', maxBytes, backupCount, 'utf-8')
        hdr = TimedRotatingFileHandler(path, 'D', 1, backupCount)
        hdr.suffix = "%Y%m%d"
        hdr.setFormatter(frt)
        hdr._name = logname + '_p'
        already_in = False
        for _hdr in logger.handlers:
            if _hdr._name == logname + '_p':
                already_in = True
                break
        if not already_in:
            logger.addHandler(hdr)
    if to_stdout:
        hdr = logging.StreamHandler(sys.stdout)
        hdr.setFormatter(frt)
        hdr._name = logname + '_s'
        already_in = False
        for _hdr in logger.handlers:
            if _hdr._name == logname + '_s':
                already_in = True
        if not already_in:
            logger.addHandler(hdr)
    if level == 'NOTEST':
        level == logging.NOTSET
    elif level == 'DEBUG':
        level == logging.DEBUG
    elif level == 'WARNING':
        level == logging.WARNING
    elif level == 'ERROR':
        level == logging.ERROR
    elif level == 'CRITICAL':
        level == logging.CRITICAL
    else:
        level == logging.INFO
    logger.setLevel(level)

    sentrykey = sentrykey.strip()
    print 'see sentry: ', sentrykey # hdr = SentryHandler('http://1d1db94883984afb8401b1c616b63922:c7cf1b896ed1465d8f047d36b0fdd268@111.innapp.cn:9090/3')
    if not sentrykey == '':
        if not '?' in sentrykey:
            sentrykey = sentrykey + '?timeout=' + str(TIMEOUT)
        elif not 'timeout=' in sentrykey.split('?')[-1]:
            sentrykey = sentrykey + '&timeout=' + str(TIMEOUT)
    hdr = SentryHandler(sentrykey)
    # setup_logging(hdr)
    # logger.addHandler(hdr)

    def _wraper(*args, **kwargs):
        if not LOGDEBUG:
            return
        if not args:
            return
        encoding = 'utf8' if os.name == 'posix' else 'gbk'
        args = [_cu(a, encoding) for a in args]
        f_back = None
        try:
            raise Exception
        except:
            f_back = sys.exc_traceback.tb_frame.f_back
        f_name = f_back.f_code.co_name
        filename = os.path.basename(f_back.f_code.co_filename)
        m_name = os.path.splitext(filename)[0]
        prefix = (u'[%s.%s]' % (m_name, f_name)).ljust(20, ' ')
        s = kwargs.get('to_sentry', False)
        if s and not sentrykey == '':
            logger.addHandler(hdr)
        else:
            logger.removeHandler(hdr)
        l = kwargs.get('printlevel', 'info').upper()
        if l == 'DEBUG':
            try:
                logger.debug(u' '.join([prefix,
                     ' '.join(args)]))
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print 'Error: %s' % ','.join(err_messages)
        elif l == 'WARNING':
            try:
                logger.warning(u' '.join([prefix,
                     ' '.join(args)]))
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print 'Error: %s' % ','.join(err_messages)
        elif l == 'ERROR':
            try:
                logger.error(u' '.join([prefix,
                         ' '.join(args)]))
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print 'Error: %s' % ','.join(err_messages)
        elif l == 'CRITICAL':
            try:
                logger.critical(u' '.join([prefix,
                     ' '.join(args)]))
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print 'Error: %s' % ','.join(err_messages)
        else:
            try:
                logger.info(u' '.join([prefix,
                     ' '.join(args)]))
            except:
                t, v, b = sys.exc_info()
                err_messages = traceback.format_exception(t, v, b)
                print 'Error: %s' % ','.join(err_messages)
    return _wraper, logger

def fileprint(filename, category, level=logging.DEBUG, maxBytes=1024*10124*100,
             backupCount=0, to_stdout=True):
    """
        生成日志输出的方法和对象
        @param filename 日志名称
        @param category 日志路径
        @param level 日志输出级别 (可选)
        @param maxBytes 日志单次输出最大长度 (可选)
        @param backupCount 日志轮询备份记录 (可选)
        @param to_stdout 是否屏幕输出 (可选)
        @return _wraper 返回日志方法
        @return filer 返回日志对象
    """
    path = os.path.join(FILEDIR, category, filename)

    # Initialize filer
    filer = logging.getLogger(filename)
    frt = logging.Formatter('%(message)s')
    hdr = None
    if path:
        hdr = RotatingFileHandler(path, 'a', maxBytes, backupCount, 'utf-8')
        hdr.setFormatter(frt)
        hdr._name = filename + '_p'
        already_in = False
        for _hdr in filer.handlers:
            if _hdr._name == filename + '_p':
                already_in = True
                break
        if not already_in:
            filer.addHandler(hdr)
    if to_stdout:
        hdr = logging.StreamHandler(sys.stdout)
        hdr.setFormatter(frt)
        hdr._name = filename + '_s'
        already_in = False
        for _hdr in filer.handlers:
            if _hdr._name == filename + '_s':
                already_in = True
        if not already_in:
            filer.addHandler(hdr)
    filer.setLevel(level)
    def _wraper(*args):
        if not LOGDEBUG:
            return
        if not args:
            return
        encoding = 'utf8' if os.name == 'posix' else 'gbk'
        args = [_cu(a, encoding) for a in args]
        filer.info(' '.join(args))
    return _wraper, filer

class bcolors:
    """
        定义常用颜色
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

if __name__ == '__main__':
    pass
