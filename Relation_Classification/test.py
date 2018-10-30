# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: test.py

@time: 18-10-23

@desc:
李白有哪些作品？
黄宗羲的著作有哪些？
李白的著作有哪些？
"""
import torch
import json
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '1'

if __name__ == '__main__':
    model = torch.load('./check_point/model.pkl')
    model.train(False)

    word2idx_path = './resources/word2idx.json'
    idx2word_path = './resources/idx2word.json'
    cat2idx_path = './resources/cat2idx.json'
    idx2cat_path = './resources/idx2cat.json'
    word2idx = json.load(open(word2idx_path, 'r', encoding='utf-8'))
    idx2word = json.load(open(idx2word_path, 'r', encoding='utf-8'))
    cat2idx = json.load(open(cat2idx_path, 'r', encoding='utf-8'))
    idx2cat = json.load(open(idx2cat_path, 'r', encoding='utf-8'))

    while True:
        print('Please Input: ')
        tokens = list(input())

        input_tensor = torch.LongTensor([word2idx.get(c, 0) for c in tokens]).view(1, -1).cuda()
        scores = model(input_tensor)
        idx = torch.argmax(scores, dim=-1).cpu().item()

        print(idx2cat[str(idx)])
        print('#' * 100)