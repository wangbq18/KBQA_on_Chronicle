# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: record.py

@time: 2018/1/4 19:48

@desc: 记录用户的交互信息，存储在本地的mongodb数据库中。

"""
import pymongo
from collections import defaultdict
import time


class Recorder:
    def __init__(self, db_name, collection_names, ip=None, port=None):
        # type: (str, dict, str, str) -> None
        """
        
        :param db_name: 
        :param collection_names: 四个collection存放对应的反馈结果
        :param ip: 
        :param port: 
        """
        self.connection = pymongo.MongoClient(host=ip, port=port)
        self.db = self.connection[db_name]
        self.success_collection = self.db[collection_names['success']]  # 得到正确的结果
        self.failure_collection = self.db[collection_names['failure']]  # 不能理解问题/不能将问题解析为SPARQL
        self.unknown_collection = self.db[collection_names['unknown']]  # 知识图谱中没有对应的结果
        self.wrong_collection = self.db[collection_names['wrong']]  # 得到错误的结果（信息错误或者解析错误）
        self.tmp_container = defaultdict(list)
        self.initial_time = time.time()

        print('MongoDB connected!')

    def clean_list(self):
        if time.time() - self.initial_time > 86400:
            tmp = defaultdict(list)
            for k, v in self.tmp_container.iteritems():
                tmp[k] = v[-1:]
            del self.tmp_container
            self.tmp_container = tmp

    def dump_to_mongodb(self, status, sparql, question, answer, user_id, approach_type):
        if status == 'failure':
            self.failure_collection.insert({'user_id': user_id, 'question': question, 'approach_type': approach_type})

        elif status == 'unknown':
            self.unknown_collection.insert({'user_id': user_id, 'question': question, 'sparql': sparql})

        else:
            # TODO 如果服务启动超过一天，清空问题缓存
            self.clean_list()

            # TODO 此用户没有提问，暂存当前问题。
            if len(self.tmp_container[user_id]) == 0:
                self.tmp_container[user_id].append((status, sparql, question, answer, user_id, approach_type))

            # TODO 用户已经提问过，把上一个问题保存到数据库中，暂存当前问题。
            else:
                self.tmp_container[user_id].append((status, sparql, question, answer, user_id, approach_type))
                _, sparql, question, answer, user_id, approach_type = self.tmp_container[user_id].pop(0)
                self.success_collection.insert({'user_id': user_id,
                                                'question': question,
                                                'sparql': sparql,
                                                'answer': answer,
                                                'approach_type': approach_type})

    def dump_wrong_record(self, user_id):
        if len(self.tmp_container[user_id]) != 0:
            _, sparql, question, answer, user_id, approach_type = self.tmp_container[user_id].pop(0)
            self.wrong_collection.insert({'user_id': user_id,
                                          'question': question,
                                          'sparql': sparql,
                                          'answer': answer,
                                          'approach_type': approach_type})
            return 'success'
        else:
            return 'fail'
