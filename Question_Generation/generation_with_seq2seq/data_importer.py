# encoding=utf-8

"""

@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: data_importer.py

@time: 8/14/18

@desc:

"""

from torch.utils.data import Dataset
import torch
import pymongo
import os
import json


class TripleQuestion(Dataset):
    def __init__(self):
        # TODO connect to mongodb and fetch triple and question
        connection = pymongo.MongoClient()
        db = connection['chronicle_training_data']
        collection = db['pattern_auto_generated_data']
        word2idx_path = './resources/word2idx.json'
        idx2word_path = './resources/idx2word.json'
        dict_exists = os.path.exists(word2idx_path)
        if dict_exists:
            self.word2idx = json.load(open(word2idx_path, 'r', encoding='utf-8'))
            self.idx2word = json.load(open(idx2word_path, 'r', encoding='utf-8'))
        else:
            self.word2idx = {'SOS': 0, 'EOS': 1, 'PAD': 2, '<S>': 3, '<P>': 4}
            self.idx2word = {0: 'SOS', 1: 'EOS', 2: 'PAD', 3: '<S>', 4: '<P>'}

        self.data = list()
        self.max_len = 0
        for i in collection.find():
            tokens = i['segmented'].split()
            # TODO replace sub predicate with placeholder
            try:
                sub_index = tokens.index(i['subject_word'])
                pre_index = tokens.index(i['predicate_word'])
                tokens[sub_index] = '<S>'
                tokens[pre_index] = '<P>'
            except ValueError:
                continue

            tokens_num = len(tokens)

            if not dict_exists:
                for w in tokens:
                    if w not in self.word2idx:
                        idx = len(self.word2idx)
                        self.word2idx[w] = idx
                        self.idx2word[idx] = w

                if i['subject_word'] not in self.word2idx:
                    idx = len(self.word2idx)
                    self.word2idx[i['subject_word']] = idx
                    self.idx2word[idx] = i['subject_word']

                if i['predicate_word'] not in self.word2idx:
                    idx = len(self.word2idx)
                    self.word2idx[i['predicate_word']] = idx
                    self.idx2word[idx] = i['predicate_word']

            self.data.append((i['subject_word'], i['predicate_word'], tokens))
            if tokens_num > self.max_len:
                self.max_len = tokens_num

        if not dict_exists:
            json.dump(self.word2idx, open(word2idx_path, 'w', encoding='utf-8'))
            json.dump(self.idx2word, open(idx2word_path, 'w', encoding='utf-8'))

    def __getitem__(self, index):
        subject_word, predicate_word, tokens = self.data[index]
        subject_word_idx = self.word2idx[subject_word]
        predicate_word_idx = self.word2idx[predicate_word]
        question_idx = [self.word2idx[t] for t in tokens] + \
                       [self.word2idx['EOS']] + \
                       [self.word2idx['PAD'] for _ in range(self.max_len - len(tokens))]
        return torch.LongTensor([subject_word_idx, predicate_word_idx]), torch.LongTensor(question_idx)

    def __len__(self):
        return len(self.data)