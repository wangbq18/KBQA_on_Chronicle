# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: data_importer.py

@time: 18-10-16

@desc:


"""
from torch.utils.data import Dataset
import torch
import pymongo
import os
import json


class QuestionTag(Dataset):
    def __init__(self):
        # TODO connect to mongodb and fetch triple and question
        connection = pymongo.MongoClient()
        db = connection['chronicle_training_data']
        collection = db['pattern_auto_generated_data']
        word2idx_path = './resources/word2idx.json'
        idx2word_path = './resources/idx2word.json'
        tag2idx_path = './resources/tag2idx.json'
        idx2tag_path = './resources/idx2tag.json'
        dict_exists = os.path.exists(word2idx_path)
        if dict_exists:
            self.word2idx = json.load(open(word2idx_path, 'r', encoding='utf-8'))
            self.idx2word = json.load(open(idx2word_path, 'r', encoding='utf-8'))
            self.tag2idx = json.load(open(tag2idx_path, 'r', encoding='utf-8'))
            self.idx2tag = json.load(open(idx2tag_path, 'r', encoding='utf-8'))
        else:
            self.word2idx = {'<unk>': 0}
            self.idx2word = {0: '<unk>'}
            self.tag2idx = {'B': 0, 'M': 1, 'E': 2, 'O': 3, '<sos>': 4, '<eos>': 5}
            self.idx2tag = {0: 'B', 1: 'M', 2: 'E', 3: 'O', 4: '<sos>', 5: '<eos>'}

        self.data = list()
        self.max_len = 0
        for i in collection.find():
            chars = list(i['question'])
            tags = list(i['question_label'])

            if not dict_exists:
                for w in chars:
                    if w not in self.word2idx:
                        idx = len(self.word2idx)
                        self.word2idx[w] = idx
                        self.idx2word[idx] = w

            self.data.append((chars, tags))

        if not dict_exists:
            json.dump(self.word2idx, open(word2idx_path, 'w', encoding='utf-8'))
            json.dump(self.idx2word, open(idx2word_path, 'w', encoding='utf-8'))
            json.dump(self.tag2idx, open(tag2idx_path, 'w', encoding='utf-8'))
            json.dump(self.idx2tag, open(idx2tag_path, 'w', encoding='utf-8'))

    def __getitem__(self, index):
        chars, tags = self.data[index]
        char_idxs = [self.word2idx[c] for c in chars]
        tag_idxs = [self.tag2idx[t] for t in tags]
        return torch.LongTensor(char_idxs), torch.LongTensor(tag_idxs)

    def __len__(self):
        return len(self.data)