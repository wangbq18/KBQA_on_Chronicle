# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: main.py

@time: 2017/12/19 20:49

@desc:

"""

import web
from web.template import render
import sys
import os

dir_path = os.path.dirname(os.path.abspath(__file__))
main_dir_path = os.path.abspath(os.path.join(dir_path, '..'))
sys.path.append(main_dir_path)

from KB_wechat import record
from KB_query import query_main
from KB_wechat.handle import Handle, QA, FeedBack


urls = (
    '/wx', 'Handle',
    '/shuchong', 'Shuchong',
    '/qa', 'QA',
    '/feedback', 'FeedBack',

)

render = web.template.render(os.path.join(main_dir_path, 'KB_wechat/templates'))


class Shuchong:
    def GET(self):
        return render.shuchong()

if __name__ == '__main__':
    dict_root_path = '/home/hsl/PycharmProjects/KBQA_on_Chronicle/KB_query/external_dict'
    ner_root_path = '/home/hsl/PycharmProjects/KBQA_on_Chronicle/NER'
    rc_root_path = '/home/hsl/PycharmProjects/KBQA_on_Chronicle/Relation_Classification'
    sys.path.append(ner_root_path)
    sys.path.append(rc_root_path)
    query = query_main.Query(dict_root_path, ner_root_path, rc_root_path)

    recorder = record.Recorder(db_name='chronicle_collected_data',
                                   collection_names={'success': 'success', 'failure': 'failure',
                                                     'unknown': 'unknown', 'wrong': 'wrong'})
    app = web.application(urls, globals())
    web.config.update({'query': query, 'recorder': recorder})
    app.run()