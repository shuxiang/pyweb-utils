#coding=utf8
from pyes import ES, Search
from pyes.exceptions import NotFoundException
import sys
import pyes
from vas.big_data.modules.orders.models import Orders, OrderUnit, OrderDetail
from sqlalchemy import and_, func, or_
from pprint import pprint
import traceback
import time
from hashlib import sha1


def _gen_cache_key(field_name, source, **kw):
    ks = kw.keys()
    ks.sort()

    _hash = sha1(("/".join([kw.get(k) for k in ks if kw.get(k)])).encode('utf8')).hexdigest()
    return '%s/%s/%s'%(field_name, source, _hash), '%s/%s/%s/code'%(field_name, source, _hash)


def unit2es(conn, _page=1):
    subq = OrderUnit.query.filter(OrderUnit.status_code!='-1').filter(OrderUnit.status!='ERROR') \
            .filter(OrderUnit.is_charge==0).filter(OrderUnit.fromCached!=1) \
            .filter(and_(OrderUnit.field_name!='region_city', OrderUnit.field_name!='region_province', OrderUnit.field_name!='operator')) \
            .order_by(OrderUnit.id.asc())
    pagin = subq.paginate(page=_page, per_page=200)
    pages = pagin.pages
    for page in range(_page, pages+1):
        pagin = subq.paginate(page=page, per_page=200)
        #try:
        for unit in pagin.items:
            d = {'complete_time':str(unit.create_time) if unit.create_time else '1970-01-01 00:00:01',
                    'source':unit.source or '',
                    'field_name':unit.field_name or '',
                    'status_code':unit.status_code or '',
                    'name':unit.name or '',
                    'mobile':unit.mobile or '',
                    'id_number':unit.id_number or '',
                    'bank_card':unit.bank_card or '',
                    'corporation':unit.corporation or '',
                    'id':_gen_cache_key(unit.field_name, unit.source, name=unit.name, id_number=unit.id_number, mobile=unit.mobile, bank_card=unit.bank_card)[0],
                    'result':unit._result or ''
                    }
            #
            try:
                conn.index(d, 'order_index', 'resource', id=d['id'])
            except:
                print '--------------------\n', d
        conn.indices.refresh('order_index')
        # except Exception as e:
        #     traceback.print_exc()
        #     print '======== ERR ========', e, page, pages
        print '------------page-------------', page, pages
        time.sleep(0.1)
        #return


def es_search(conn, start=0, size=20, doc_types='resource', indices='order_index', sort=None, **kwargs):

    # set filter
    filters = []
    for k,v in kwargs.items():
        if k and v!='' and k!='complete_time':
            filters.append(pyes.filters.TermFilter(k, v))
        elif k and v!='' and k=='complete_time':
            ct = kwargs['complete_time']
            if len(ct) == 2:
                filters.append(pyes.filters.RangeFilter(pyes.ESRange('complete_time', from_value=ct[0], to_value=ct[1])))
            else:
                filters.append(pyes.filters.RangeFilter(pyes.ESRange('complete_time', from_value=ct[0])))
    
    _filter = None
    if filters:
        _filter = pyes.filters.ANDFilter(filters)

    bq = pyes.MatchAllQuery()
    # filtered
    q = pyes.FilteredQuery(bq, _filter)

    # sort
    if sort:
        sf = pyes.sort.SortFactory()
        for s in sort:
            sf.add(s)
        s = Search(q, sort=sf)
    else:
        s = Search(q)

    # result
    return conn.search(s, indices=indices, doc_types=doc_types, start=start, size=size)

def es_delete(conn, index='order_index', doc_type='resource', id=''):
    return conn.delete(index=index, doc_type=doc_type, id=id)

def es_create(conn, index='order_index', doc_type='resource', doc=None):
    try:
        es_delete(conn, index, doc_type, doc['id'])
    except NotFoundException:
        pass
    try:
        return conn.index(doc, index, doc_type, id=doc['id'])
    except:# not connection
        pass

if __name__ == '__main__':
    conn = ES('127.0.0.1:9200')

    # manage.py dir
    sys.path.append('/home/sx/epan/bigData')
    from manage import app
    #with app.test_request_context('/test_ctx_of_workers/'):
    #   unit2es(conn, _page=1871)
    for m in es_search(conn, mobile=u'13167077911'):
        pprint(m)
    print '----'
    for m in es_search(conn, name=u'刘胜久'):
        pprint(m)
    print '----'
    for m in es_search(conn, complete_time=['2016-12-01 01:07:27'], name=u'刘胜久'):
        pprint(m)
    print '-----'
    for m in es_search(conn, complete_time=['2016-08-21 01:01:01'], sort=[pyes.sort.SortOrder(field='complete_time', order='desc')]):
        print m
    # sh bin/elasticsearch -d

    """/* http://127.0.0.1:9200/order_index //doc_type=resource doc_name=order_index put=create, delete=delete*/

    {
      "settings": {
         "refresh_interval": "5s",
         "number_of_shards" :   1,
         "number_of_replicas" : 0
      },
      "mappings": {
        "_default_":{
          "_all": { "enabled":  false }
        },
        "resource": {
          "dynamic": false,
          "properties": {
            "complete_time": {
              "type": "date",
              "format": "yyyy-MM-dd HH:mm:ss"
            },
            "field_name": {
              "type": "string",
              "index": "not_analyzed"
            },
            "id":{
              "type": "string",
              "index": "not_analyzed"
            },
            "source": {
              "type": "string",
              "index": "not_analyzed"
            },
            "name": {
              "type": "string",
              "index": "not_analyzed"
            },
            "mobile": {
              "type": "string",
              "index": "not_analyzed"
            },
            "id_number": {
              "type": "string",
              "index": "not_analyzed"
            },
            "bank_card": {
              "type": "string",
              "index": "not_analyzed"
            },
            "status_code": {
              "type": "string",
              "index": "not_analyzed"
            },
            "corporation": {
              "type": "string",
              "index": "analyzed",
              "fields": {
                "cn": {
                  "type": "string",
                  "analyzer": "ik"
                },
                "en": {
                  "type": "string",
                  "analyzer": "english"
                }
              }
            },
            "result": {
              "type": "string",
              "index": "analyzed",
              "fields": {
                "cn": {
                  "type": "string",
                  "analyzer": "ik"
                },
                "en": {
                  "type": "string",
                  "analyzer": "english"
                }
              }
            }
          }
        }
      }
    }
    """