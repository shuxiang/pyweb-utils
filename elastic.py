#coding=utf8

from pyes import ES, Search
from pyes.exceptions import NotFoundException
from pyes import ESRange, MatchAllQuery, FilteredQuery
from pyes.filters import RangeFilter,TermFilter, ANDFilter
from pyes.sort import SortFactory

class Elastic(object):

    def init_app(self, app):
        self.conn = ES(app.config['ELASTIC_URL'], timeout=2)
        #self.remote_conns = [ES(url) for url in app.config['REMOTE_ELASTIC_URL']]

    def search(self, start=0, size=20, doc_types='resource', indices='order_index', sort=None, **kwargs):
        # set filter
        filters = []
        for k,v in kwargs.items():
            if k and k!='complete_time':
                filters.append(TermFilter(k, v))
            elif k and v!='' and k=='complete_time':
                ct = kwargs['complete_time']
                if len(ct) == 2:
                    filters.append(RangeFilter(ESRange('complete_time', from_value=ct[0], to_value=ct[1])))
                else:
                    filters.append(RangeFilter(ESRange('complete_time', from_value=ct[0])))
        
        _filter = None
        if filters:
            _filter = ANDFilter(filters)

        bq = MatchAllQuery()
        # filtered
        q = FilteredQuery(bq, _filter)

        # sort
        if sort:
            sf = SortFactory()
            for s in sort:
                sf.add(s)
            s = Search(q, sort=sf)
        else:
            s = Search(q)

        # result
        return self.conn.search(s, indices=indices, doc_types=doc_types, start=start, size=size)

    def delete(self, index='order_index', doc_type='resource', id=''):
        return self.conn.delete(index=index, doc_type=doc_type, id=id)

    def create(self, index='order_index', doc_type='resource', doc=None):
        # try:
        #     self.delete(index, doc_type, doc['id'])
        # except NotFoundException:
        #     pass
        try:
            return self.conn.index(doc, index, doc_type, id=doc['id'])
        except:# not connection
            pass

    def multi_create(self, index='order_index', doc_type='resource', doc=None):
        """如果同步缓存到远程，要使用celery"""
        try:
            return self.conn.index(doc, index, doc_type, id=doc['id'])
        except:# not connection
            pass
            
        try:
            for rconn in self.remote_conns:
                rconn.index(doc, index, doc_type, id=doc['id'])
        except:
            print '--------sync cache to remote error------'

        


elastic = Elastic()
