#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import absolute_import

import logging
from logging.handlers import RotatingFileHandler

from flask import current_app
from ..utils.utils import *
from ..utils.log import initLogger

FORMAT = logging.Formatter(
    '%(asctime)s:[%(levelname)s]%(name)s:%(pathname)s#%(lineno)d: %(message)s'
)


def stream_handler(level):
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(FORMAT)
    return handler


def file_handler(level,log_file):
    handler = RotatingFileHandler(log_file,
                                  maxBytes=1024 * 1024 * 200,
                                  backupCount=100)
    handler.setLevel(level)
    handler.setFormatter(FORMAT)
    return handler

#def initFlaskLogger():

#    try:
#        logger = current_app.logger
#        log_level = current_app.config.pop('LOG_LEVEL', logging.INFO)
#        log_file = current_app.config.pop('LOG_FILE', logFileFullPath)
        # assert log_file, 'LOG_FILE has not benn configured'
#        logger.setLevel(log_level)
#        logger.addHandler(file_handler(log_file=log_file))
#        logger.info('Flask Logger inited')
#    except RuntimeError,e:
#        logger = initLogger()
#        logger.error("current_app.logger error:%s" % e.message)
#        logger.error("get logger of flask app is error!So now we use standard logger!")

#        pass
#    finally:
#        return logger
#       pass

#    pass

class FlaskLogger(object):
    def __int__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        log_level = app.config.pop('LOG_LEVEL', logging.INFO)
        log_file = app.config.pop('LOG_FILE', None)
        assert log_file, 'LOG_FILE has not benn configured'
        app.logger.addHandler(file_handler(level=log_level, log_file=log_file))

    @property
    def __logger(self):
        # 继承flask.current_app 的线程安全特性
        try:
            logger = current_app.logger
        except RuntimeError:
            logger = self.app.logger
        return logger

    def debug(self, msg, *args, **kwargs):
        return self.__logger.debug(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return self.__logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        return self.__logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self.__logger.error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        return self.__logger.critical(msg, *args, **kwargs)

#logger =#FlaskLogger()  initFlaskLogger()
logger =initLogger()
