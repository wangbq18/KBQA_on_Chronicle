# encoding=utf-8

"""

@author: SimmerChan

@contact: 7698590@qq.com

@file: word_tagging.py

@time: 2017/12/6 13:50

@desc: 利用nlpir工具对问句进行分词和词性标记，并返回词对象

"""

import jieba
import jieba.posseg as pseg


class Word(object):
    def __init__(self, token, pos):
        self.token = token
        self.pos = pos


class TaggedWords:
    def __init__(self, dict_path):
        for path in dict_path:
            jieba.load_userdict(path)
        jieba.suggest_freq(('哪些', '地方'), True)
        jieba.suggest_freq(('去', '过'), True)

    @staticmethod
    def get_word_objects(sentence):
        # type: (str) -> list
        """

        :param sentence:
        :return:
        """
        # TODO for python 2.7
        # wo = [Word(word.encode('utf-8'), tag) for word, tag in pseg.cut(sentence)]

        # TODO for python 3+
        wo = [Word(word, tag) for word, tag in pseg.cut(sentence)]
        return wo


# if __name__ == '__main__':
#     tagger = TaggedWords(1)
#     for i in tagger.get_word_objects('演了哪些喜剧电影？'):
#         print i.token, i.pos