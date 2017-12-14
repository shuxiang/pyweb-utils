/* http://127.0.0.1:9200/order_index //doc_type=resource doc_name=order_index put=create, delete=delete*/
{
  "settings": {
     "refresh_interval": "5s", // 创建索引时，flush到磁盘的时间间隔
     "number_of_shards" :   1, // 一个主节点
     "number_of_replicas" : 0 // 0个副本，后面可以加
  },
  "mappings": {
    "_default_":{
      "_all": { "enabled":  false } // 关闭_all字段，因为我们只搜索title字段
    },
    "resource": {
      "dynamic": false, // 关闭“动态修改索引”
      "properties": {
        "order_id": {
          "type": "integer"
        },
        "serial_number": {
          "type": "string",
          "index": "not_analyzed"
        },
        "user_id": {
          "type": "integer"
        },
        "complete_time": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "case_id": {
          "type": "string",
          "index": "not_analyzed"
        },
        "field_name": {
          "type": "string",
          "index": "not_analyzed"
        },
        "status":{
          "type": "string",
          "index": "not_analyzed"
        },
        "unit_id":{
          "type": "integer"
        },
        "fromCached": {
          "type": "integer"
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
        "is_charge": {
          "type": "integer"
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

/*
body = """
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
        "order_id": {
          "type": "integer"
        },
        "serial_number": {
          "type": "string",
          "index": "not_analyzed"
        },
        "user_id": {
          "type": "integer"
        },
        "complete_time": {
          "type": "date",
          "format": "yyyy-MM-dd HH:mm:ss"
        },
        "case_id": {
          "type": "string",
          "index": "not_analyzed"
        },
        "field_name": {
          "type": "string",
          "index": "not_analyzed"
        },
        "status":{
          "type": "string",
          "index": "not_analyzed"
        },
        "unit_id":{
          "type": "integer"
        },
        "fromCached": {
          "type": "integer"
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
        "is_charge": {
          "type": "integer"
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
from pprint import pprint
import json
import requests
import httplib
c =  httplib.HTTPConnection('127.0.0.1:9200')
c.request('PUT', '/order_index', body)

requests.delete('http://127.0.0.1:9200/order_index').content

body = """
{
  "query": {
    "filtered": {
      "query": {
        "match_all": {}
      },
      "filter": {
        "geo_distance": {
          "distance": "20miles",
          "location": {
            "lat": 36.67160269887686,
            "lon": 117.01681051591959
          }
        }
      }
    }
  }
}
"""
c.request('POST', '/order_index/_search', body)

c.request('GET', '/_nodes/stats', '')

c.request('GET', '/order_index/_stats', '')

r = c.getresponse().read()
pprint(json.loads(r))
*/