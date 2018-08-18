# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: sparql_endpoint.py

@time: 2018/7/8 15:50

@desc:

"""
# encoding=utf-8

"""

@author: SimmerChan

@contact: 7698590@qq.com

@file: jena_sparql_endpoint.py

@time: 2017/11/30 13:53

@desc:从jena的fuseki进行sparql查询

"""
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import OrderedDict


# server ip 10.15.82.114
class JenaFuseki:
    def __init__(self, endpoint_url='http://localhost:3030/chronicle_kg/query'):
        self.sparql_conn = SPARQLWrapper(endpoint_url)

    def get_sparql_result(self, query):
        self.sparql_conn.setQuery(query)
        self.sparql_conn.setReturnFormat(JSON)
        return self.sparql_conn.query().convert()

    @staticmethod
    def parse_result_into_list(query_result):
        query_head = query_result['head']['vars']
        query_results = list()
        # print query_result
        for r in query_result['results']['bindings']:
            temp_dict = OrderedDict()
            # print query_head
            # print r
            for h in query_head:
                try:
                    temp_dict[h] = r[h]['value']
                except KeyError:
                    continue
            query_results.append(temp_dict)
        return query_head, query_results

    def print_result_to_string(self, query_result):
        query_head, query_results = self.parse_result_into_list(query_result)
        for h in query_head:
            print h, ' '*5,
        print
        for qr in query_results:
            for _, value in qr.iteritems():
                print value, ' ',
            print

    def get_sparql_result_value(self, query_result):
        _, query_results = self.parse_result_into_list(query_result)
        values = list()
        for qr in query_results:
            for _, value in qr.iteritems():
                values.append(value)
        return values

if __name__ == '__main__':
    fuseki = JenaFuseki()
    my_query = """
PREFIX : <http://www.cadal.zju.edu.cn/bns/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?o ?n WHERE {?s :hasAuthor ?x . ?x :personName ?o. ?s :textTitle ?n.}
limit 10
    """
    result = fuseki.get_sparql_result(my_query)
    fuseki.print_result_to_string(result)
    # for i in fuseki.get_sparql_result_value(result):
    #     print i
