# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: data_importer.py

@time: 18-10-23

@desc:


"""
from torch.utils.data import Dataset
import torch
import pymongo
import os
import json


class QuestionType(Dataset):
    def __init__(self):
        # TODO connect to mongodb and fetch triple and question
        connection = pymongo.MongoClient()
        db = connection['chronicle_training_data']
        collection = db['pattern_auto_generated_data']
        word2idx_path = './resources/word2idx.json'
        idx2word_path = './resources/idx2word.json'
        cat2idx_path = './resources/cat2idx.json'
        idx2cat_path = './resources/idx2cat.json'
        dict_exists = os.path.exists(word2idx_path)

        if dict_exists:
            self.word2idx = json.load(open(word2idx_path, 'r', encoding='utf-8'))
            self.idx2word = json.load(open(idx2word_path, 'r', encoding='utf-8'))
            self.cat2idx = json.load(open(cat2idx_path, 'r', encoding='utf-8'))
            self.idx2cat = json.load(open(idx2cat_path, 'r', encoding='utf-8'))
        else:
            self.word2idx = {'<unk>': 0, 'PAD': 1}
            self.idx2word = {0: '<unk>', 1: 'PAD'}
            self.cat2idx = {}
            self.idx2cat = {}

        self.data = list()
        self.max_len = 0

        for i in collection.find():
            tokens = list(i['question'])
            category = i['predicate']

            tokens_num = len(tokens)

            if not dict_exists:
                for w in tokens:
                    if w not in self.word2idx:
                        idx = len(self.word2idx)
                        self.word2idx[w] = idx
                        self.idx2word[idx] = w

                if category not in self.cat2idx:
                    idx = len(self.cat2idx)
                    self.cat2idx[category] = idx
                    self.idx2cat[idx] = category

            self.data.append((tokens, category))

            if tokens_num > self.max_len:
                self.max_len = tokens_num

        if not dict_exists:
            json.dump(self.word2idx, open(word2idx_path, 'w', encoding='utf-8'))
            json.dump(self.idx2word, open(idx2word_path, 'w', encoding='utf-8'))
            json.dump(self.cat2idx, open(cat2idx_path, 'w', encoding='utf-8'))
            json.dump(self.idx2cat, open(idx2cat_path, 'w', encoding='utf-8'))

    def __getitem__(self, index):
        tokens, category = self.data[index]
        category_idx = self.cat2idx[category]
        question_idx = [self.word2idx[t] for t in tokens] + \
                       [self.word2idx['PAD'] for _ in range(self.max_len - len(tokens))]
        return torch.LongTensor(question_idx), torch.LongTensor([category_idx])

    def __len__(self):
        return len(self.data)