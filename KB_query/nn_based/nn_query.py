# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: nn_query.py

@time: 18-10-30

@desc:

李白的作品是什么
"""
import torch
import json
import os
import sys


class NNQury(object):
    def __init__(self):
        ner_model_path = '../../NER/check_point/model.pkl'
        relation_model_path = '../../Relation_Classification/check_point/model.pkl'
        sys.path.append('../../NER')
        sys.path.append('../../Relation_Classification')
        if not os.path.exists(ner_model_path) or not os.path.exists(relation_model_path):
            raise ValueError("Model doesn't exist!")

        self.ner_model = torch.load(ner_model_path)
        self.relation_model = torch.load(relation_model_path)
        self.ner_model.train(False)
        self.ner_model.lstm.flatten_parameters()
        self.relation_model.train(False)

        rc_word2idx_path = '../../Relation_Classification/resources/word2idx.json'
        rc_idx2word_path = '../../Relation_Classification/resources/idx2word.json'
        rc_cat2idx_path = '../../Relation_Classification/resources/cat2idx.json'
        rc_idx2cat_path = '../../Relation_Classification/resources/idx2cat.json'
        ner_word2idx_path = '../../NER/resources/word2idx.json'
        ner_idx2word_path = '../../NER/resources/idx2word.json'
        ner_tag2idx_path = '../../NER/resources/tag2idx.json'
        ner_idx2tag_path = '../../NER/resources/idx2tag.json'
        self.rc_word2idx = json.load(open(rc_word2idx_path, 'r', encoding='utf-8'))
        self.rc_idx2word = json.load(open(rc_idx2word_path, 'r', encoding='utf-8'))
        self.rc_cat2idx = json.load(open(rc_cat2idx_path, 'r', encoding='utf-8'))
        self.rc_idx2cat = json.load(open(rc_idx2cat_path, 'r', encoding='utf-8'))
        self.ner_word2idx = json.load(open(ner_word2idx_path, 'r', encoding='utf-8'))
        self.ner_idx2word = json.load(open(ner_idx2word_path, 'r', encoding='utf-8'))
        self.ner_tag2idx = json.load(open(ner_tag2idx_path, 'r', encoding='utf-8'))
        self.ner_idx2tag = json.load(open(ner_idx2tag_path, 'r', encoding='utf-8'))

    def parse(self, question):
        chars = list(question)

        # TODO NER
        input_tensor = torch.LongTensor([self.ner_word2idx.get(c, 0) for c in chars]).view(-1, 1).cuda()
        _, tags = self.ner_model(input_tensor)
        entities = list()
        start = -1
        for index, t in enumerate(tags):
            if t == self.ner_tag2idx['B']:
                start = index
            if t == self.ner_tag2idx['O']:
                if start != -1:
                    entities.append(question[start:index])
                    start = -1

        print(entities)

        # TODO Relation Classification
        input_tensor = torch.LongTensor([self.rc_word2idx.get(c, 0) for c in chars]).view(1, -1).cuda()
        scores = self.relation_model(input_tensor)
        idx = torch.argmax(scores, dim=-1).cpu().item()

        print(self.rc_idx2cat[str(idx)])