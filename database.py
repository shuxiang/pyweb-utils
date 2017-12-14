#!/usr/bin/env python
# -*- coding:utf-8 -*-

from __future__ import absolute_import

import json
import uuid
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import types
from ..utils import sha1sum


class JSONEncodedDict(types.TypeDecorator):
    """
    Represents an immutable structure as a json-encoded string.

    Usage::

        database.JSONEncodedDict(255)

    """

    impl = types.TEXT

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class ChoiceType(types.TypeDecorator):
    """
    example::
    choices=(
        ('key1', 'value1'),
        ('key2', 'value2')
    )

    filed::
        db.Column(db.ChoiceType(length=xx, choices=choices))

    """
    impl = types.String

    def __init__(self, choices, **kw):
        self.choices = dict(choices)
        super(ChoiceType, self).__init__(**kw)

    def process_bind_param(self, value, dialect):
        return [k for k, v in self.choices.iteritems() if k == value][0]

    def process_result_value(self, value, dialect):
        return self.choices[value]


class Password(types.TypeDecorator):
    """
    这是password字段类型。就不需要到处都是加密操作了
    """
    impl = types.String

    def process_bind_param(self, value, dialect):
        return sha1sum(value) if value else None


class UUID(types.TypeDecorator):
    """Platform-independent GUID type.

    Uses Postgresql's UUID type, otherwise uses CHAR(36), storing as
    stringified hex values.

    This implementation is based on the SQLAlchemy
    `backend-agnostic GUID Type
    <http://www.sqlalchemy.org/docs/core/types.html#backend-agnostic-guid-type>`_
    example.
    """
    impl = types.String

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(db.postgresql.UUID())
        else:
            return dialect.type_descriptor(types.CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return str(uuid.uuid4())
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                # hexstring
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)


class DataBase(SQLAlchemy):
    ChoiceType = ChoiceType
    JSONEncodedDict = JSONEncodedDict
    Password = Password
    UUID = UUID

    def init_app(self, app):
        """需要用到。要不sqlalchemy部分功能无法正常使用"""
        self.app = app
        super(DataBase, self).init_app(app)

    @staticmethod
    def get_or_create(model, defaults=None, **kwargs):
        """
        获取或者创建对象，模仿django的。
        """
        instance = model.query.filter_by(**kwargs).first()
        defaults = bool(defaults) and defaults or {}
        if instance:
            setattr(instance, 'is_new', False)
        else:
            kwargs.update(defaults)
            instance = model(**kwargs)
            db.session.add(instance)
            db.session.commit()
            setattr(instance, 'is_new', True)
        return instance

db = DataBase()


class Model(db.Model):
    __abstract__ = True
    __table_args__ = {
        'mysql_engine': 'InnoDB',
        'mysql_charset': 'utf8',
    }

    @property
    def _columns_name(self):
        return [columns_name.name for columns_name in self.__table__.columns]

db.Model = Model

get_pages = lambda c, p:  c / p + 1 if c % p > 0 else c / p

class Paginate(object):
    def __init__(self, data, page=1, per_page=10):
        self.data = data
        self.total = len(data)
        self.page = page
        self.per_page = per_page
        self.pages = get_pages(self.total, self.per_page)

    @property
    def items(self):
        return self.data[(self.page-1)*self.per_page: self.page*self.per_page]

db.paginate = Paginate