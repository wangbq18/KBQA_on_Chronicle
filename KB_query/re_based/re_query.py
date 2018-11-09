# encoding=utf-8

"""

@author: SimmerChan

@contact: 7698590@qq.com

@file: nn_query.py

@time: 2017/12/6 15:56

@desc: 通过jena fuseki进行查询

"""
from KB_query.re_based import jena_sparql_endpoint
from KB_query.re_based import question2sparql
import random
import os


class REQuery:
    def __init__(self, dict_root_path):
        dict_path = [os.path.join(dict_root_path, dict_name) for dict_name in ['office_title.txt', 'person_name.txt', 'place_name.txt']]
        self.q2s = question2sparql.Question2Sparql(dict_path)
        self.fuseki = jena_sparql_endpoint.JenaFuseki()

        print('Sparql endpoint starts successfully!')

    def get_response(self, question):
        my_query = self.q2s.get_sparql(question)

        if my_query is not None:
            result = self.fuseki.get_sparql_result(my_query)
            values = self.fuseki.get_sparql_result_value(result)
            if len(values) == 0:
                return 'unknown', my_query, None
            elif len(values) == 1:
                return 'success', my_query, values[0]
            else:
                output = ''
                if len(values) > 20:
                    values = random.sample(values, 15)
                for v in values:
                    output += v + u'、'
                return 'success', my_query, output[0:-1]
        else:
            return 'failure', my_query, None


if __name__ == '__main__':
    q2s = question2sparql.Question2Sparql(['./external_dict/office_title.txt', './external_dict/person_name.txt', './external_dict/place_name.txt'])
    fuseki = jena_sparql_endpoint.JenaFuseki()

    unknown_responses = [
        u'我现在还不知道，等我多学一点再告诉你。  ;-)',
        u'渊博如我竟也不知道，你该不是刁难我吧。。。'
    ]

    cant_understand_responses = [
        u'不是我不知道，只是我现在还没办法理解你的意思。:-(',
        u'不好意思，我还没办法理解你的问题。:-('
    ]

    while True:
        question = input()
        my_query = q2s.get_sparql(question.decode('utf-8'))
        if my_query is not None:
            print(my_query)
            # exit()

            result = fuseki.get_sparql_result(my_query)
            values = fuseki.get_sparql_result_value(result)
            if len(values) == 0:
                print(random.choice(unknown_responses))
            elif len(values) == 1:
                print(values[0])
            else:
                output = ''
                for v in values:
                    output += v + u'、'
                print(output[0:-1])
        else:
            print(random.choice(cant_understand_responses))

        print('#' * 100)