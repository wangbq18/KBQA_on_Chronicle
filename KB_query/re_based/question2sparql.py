# encoding=utf-8

"""

@author: SimmerChan

@contact: 7698590@qq.com

@file: question2sparql.py

@time: 2017/12/6 15:23

@desc: 将自然语言转为sparql查询语句

"""
from KB_query.re_based import question_temp
from KB_query.re_based import word_tagging


class Question2Sparql:
    def __init__(self, dict_path):
        self.tw = word_tagging.TaggedWords(dict_path)
        self.rules = question_temp.rules

    def get_sparql(self, question):
        word_objects = self.tw.get_word_objects(question)
        queries_dict = dict()

        for index, rule in enumerate(self.rules):
            query, num = rule.apply(word_objects)

            if query is not None:
                queries_dict[num] = query

        if len(queries_dict) == 0:
            return None
        elif len(queries_dict) == 1:
            return list(queries_dict.values())[0]
        else:
            # TODO 匹配多个语句，以匹配关键词最多的句子作为返回结果
            sorted_dict = sorted(queries_dict.items(), key=lambda item: item[1])
            # print 'yes'
            # print sorted_dict
            return sorted_dict[0][1]
