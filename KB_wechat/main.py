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

from KB_query.re_based import re_query
import record


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
    web.query = re_query.Query([os.path.join(main_dir_path, 'KB_query/external_dict/office_title.txt'),
                                os.path.join(main_dir_path, 'KB_query/external_dict/person_name.txt'),
                                os.path.join(main_dir_path, 'KB_query/external_dict/place_name.txt')])
    web.recorder = record.Recorder(db_name='chronicle_collected_data',
                                   collection_names={'success': 'success', 'failure': 'failure',
                                                     'unknown': 'unknown', 'wrong': 'wrong'})
    app = web.application(urls, globals())
    app.run()