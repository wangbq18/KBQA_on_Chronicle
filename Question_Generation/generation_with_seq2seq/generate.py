# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: generate.py

@time: 18-8-19

@desc:

李白 作品
李白 妻子
"""

import torch
from model import EncoderRNN, DecoderRNN
import json
import os

os.environ['CUDA_VISIBLE_DEVICES'] = '1'
SOS_TOKEN = 0
EOS_TOKEN = 1

encoder = torch.load('./check_point/encoder.pkl')
decoder = torch.load('./check_point/decoder.pkl')
encoder.train(False)
decoder.train(False)
encoder.gru_layer.flatten_parameters()
decoder.gru_layer.flatten_parameters()

word2idx_path = './resources/word2idx.json'
idx2word_path = './resources/idx2word.json'
word2idx = json.load(open(word2idx_path, 'r', encoding='utf-8'))
idx2word = json.load(open(idx2word_path, 'r', encoding='utf-8'))

while True:
    print('Please Input: ')
    subject_word, predicate_word = input().split()
    generated_question = list()

    input_tensor = torch.LongTensor([word2idx[subject_word], word2idx[predicate_word]]).view(1, -1).cuda()
    encoder_hidden = encoder.init_hidden(1)
    encoder_outputs, encoder_hidden = encoder(input_tensor, encoder_hidden)

    decoder_input = torch.LongTensor([[SOS_TOKEN]]).view(1, 1).cuda()
    decoder_hidden = encoder_hidden
    while True:
        decoder_outputs, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden, encoder_outputs)
        topv, topi = decoder_outputs.topk(1, dim=-1)
        decoder_input = topi.view(1, -1).detach()  # TODO detach from history as input
        current_word = idx2word[str(decoder_input.squeeze().item())]
        if (current_word in ['EOS', 'PAD']) or len(generated_question) > 10:
            break
        generated_question.append(current_word)
    sentence = ''.join(generated_question)
    sentence = sentence.replace('<S>', subject_word)
    sentence = sentence.replace('<P>', predicate_word)
    print(sentence)
    print('#' * 100)