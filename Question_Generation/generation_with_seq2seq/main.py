# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: main.py

@time: 18-8-19

@desc:


"""

from data_importer import TripleQuestion
from torch.utils.data import DataLoader
from model import EncoderRNN, DecoderRNN
import torch
import torch.optim as optim
import torch.nn as nn
import random
import time
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '1'
SOS_TOKEN = 0
EOS_TOKEN = 1
log_interval = 50


def train(epoch, data, encoder, decoder, encoder_op, decoder_op, criterion):
    total_loss = 0.
    batches = len(data)
    for index, sample in enumerate(data):
        loss = 0
        encoder_op.zero_grad()
        decoder_op.zero_grad()

        sources, targets = sample
        sources, targets = sources.cuda(), targets.cuda()

        encoder_hidden = encoder.init_hidden(sources.size(0))

        # TODO encode
        encoder_outputs, encoder_hidden = encoder(sources, encoder_hidden)

        # TODO decode
        decoder_input = torch.LongTensor([[SOS_TOKEN] * sources.size(0)]).cuda()
        decoder_hidden = encoder_hidden

        use_teacher_forcing = True if random.random() < 0.5 else False

        if use_teacher_forcing:
            for i in range(targets.size(1)):
                decoder_outputs, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden,
                                                                             encoder_outputs)
                loss += criterion(decoder_outputs.squeeze(), targets[:, i])
                decoder_input = targets[:, i].view(1, -1)  # TODO teacher forcing

        else:
            for i in range(targets.size(1)):
                decoder_outputs, decoder_hidden, decoder_attention = decoder(decoder_input, decoder_hidden,
                                                                             encoder_outputs)
                topv, topi = decoder_outputs.topk(1, dim=-1)
                decoder_input = topi.view(1, -1).detach()     # TODO detach from history as input
                loss += criterion(decoder_outputs.squeeze(), targets[:, i])

        if index % log_interval == 0:
            print('Epoch:{0}-{1}/{2}, Batch Loss:{3}'.format(epoch, index, batches, loss.item()/sources.size(0)))

        loss.backward()
        total_loss += loss.item()
        encoder_op.step()
        decoder_op.step()

    return total_loss

if __name__ == '__main__':
    epochs = 5
    bs = 64
    hidden_dim = 300
    lr = 0.01
    dataset = TripleQuestion()
    dataloader = DataLoader(dataset, batch_size=bs, shuffle=True)

    vocab_size = len(dataset.word2idx)
    rnn_encoder = EncoderRNN(vocab_size, hidden_dim).cuda()
    rnn_decoder = DecoderRNN(vocab_size, hidden_dim).cuda()

    rnn_encoder_optim = optim.SGD(rnn_encoder.parameters(), lr=lr)
    rnn_decoder_optim = optim.SGD(rnn_decoder.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()

    start = time.time()
    for epoch in range(1, epochs + 1):
        loss = train(epoch, dataloader, rnn_encoder, rnn_decoder, rnn_encoder_optim, rnn_decoder_optim, criterion)
        print('Epoch:{0}, Loss:{1}, Elapsed-time:{2}'.format(epoch, loss/len(dataset), round(time.time()-start, 2)))
        print('#' * 100)

    torch.save(rnn_encoder, './check_point/encoder.pkl')
    torch.save(rnn_decoder, './check_point/decoder.pkl')