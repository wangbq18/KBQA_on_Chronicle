# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: test.py

@time: 18-10-17

@desc:
李白的作品是什么
"""
import torch
import json
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '1'

if __name__ == '__main__':
    model = torch.load('./check_point/model.pkl')
    model.train(False)
    model.lstm.flatten_parameters()

    word2idx_path = './resources/word2idx.json'
    idx2word_path = './resources/idx2word.json'
    tag2idx_path = './resources/tag2idx.json'
    idx2tag_path = './resources/idx2tag.json'
    word2idx = json.load(open(word2idx_path, 'r', encoding='utf-8'))
    idx2word = json.load(open(idx2word_path, 'r', encoding='utf-8'))
    tag2idx = json.load(open(tag2idx_path, 'r', encoding='utf-8'))
    idx2tag = json.load(open(idx2tag_path, 'r', encoding='utf-8'))

    while True:
        print('Please Input: ')
        chars = list(input())
        generated_question = list()

        input_tensor = torch.LongTensor([word2idx.get(c, 0) for c in chars]).view(-1, 1).cuda()

        score, tags = model(input_tensor)

        print(score, tags)