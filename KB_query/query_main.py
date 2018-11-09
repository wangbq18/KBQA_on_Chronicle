# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: nn_query.py

@time: 18-10-30

@desc:
黄宗羲的著作有哪些？
李白有哪些作品？
李白的著作有哪些？
杨维的父亲是谁？
郑元将的儿子是谁？
"""
from KB_query.nn_based.nn_query import NNQuery
from KB_query.re_based.re_query import REQuery
import random


class Query(object):
    def __init__(self, dict_root_path, ner_root_path, rc_root_path):
        self.nn_query = NNQuery(ner_root_path, rc_root_path)
        self.re_query = REQuery(dict_root_path)

        self.unknown_responses = [
            '我现在还不知道，等我多学一点再告诉你。  ;-)',
            '渊博如我竟也不知道，你该不是刁难我吧。。。'
        ]

        self.cant_understand_responses = [
            '不是我不知道，只是我现在还没办法理解你的意思。:-(',
            '不好意思，我还没办法理解你的问题。:-('
        ]

    def get_response(self, question):
        # TODO parse question and fetch answer with regular expression
        status, sparql, content = self.re_query.get_response(question)
        if status == 'success':
            return status, sparql, content, 're-based'
        elif status == 'unknown':
            return status, sparql, random.choice(self.unknown_responses), 're-based'

        # TODO if fail to parse question with rule-based approach, try NN-based model
        status, sparql, content = self.nn_query.get_response(question)
        return status, sparql, content, 'nn-based'

