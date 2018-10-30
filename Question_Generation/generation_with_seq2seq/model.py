# encoding=utf-8
"""
@author: SimmerChan

@contact: hsl7698590@gmail.com

@file: model.py

@time: 18-8-19

@desc:


"""
import torch
import torch.nn as nn
import torch.nn.functional as F


class EncoderRNN(nn.Module):
    def __init__(self, input_vocabulary_size, hidden_size):
        super(EncoderRNN, self).__init__()
        self.hidden_size = hidden_size

        self.embedding_layer = nn.Embedding(input_vocabulary_size, hidden_size)
        self.gru_layer = nn.GRU(hidden_size, hidden_size, batch_first=True)

    def forward(self, inputs, hidden):
        embedded = self.embedding_layer(inputs)
        outputs, hidden = self.gru_layer(embedded, hidden)
        return outputs, hidden

    def init_hidden(self, bs):
        return torch.zeros(1, bs, self.hidden_size).cuda()


class DecoderRNN(nn.Module):
    def __init__(self, output_vocabulary_size, hidden_size):
        super(DecoderRNN, self).__init__()
        self.hidden_size = hidden_size

        self.embedding_layer = nn.Embedding(output_vocabulary_size, hidden_size)
        self.attn_layer = nn.Linear(self.hidden_size * 2, 2)
        self.attn_combine_layer = nn.Linear(self.hidden_size * 2, self.hidden_size)
        self.gru_layer = nn.GRU(hidden_size, hidden_size, batch_first=True)
        self.out_layer = nn.Linear(hidden_size, output_vocabulary_size)
        self.softmax_layer = nn.LogSoftmax(dim=-1)
        self.drop_out = nn.Dropout(0.5)

    def forward(self, inputs, hidden, encoder_outputs):
        bs = inputs.size(1)
        # TODO (1, bs) -> (1, bs, hidden)
        output = self.embedding_layer(inputs)
        output = self.drop_out(output)

        attn_weights = F.softmax(self.attn_layer(torch.cat((output, hidden), -1)), dim=-1).view(bs, 1, -1)
        attn_applied = torch.bmm(attn_weights, encoder_outputs)

        output = torch.cat((output.view(bs, 1, -1), attn_applied), -1)
        output = self.attn_combine_layer(output)

        output = F.relu(output)
        output, hidden = self.gru_layer(output, hidden)

        output = self.out_layer(output)

        output = self.softmax_layer(output)

        return output, hidden, attn_weights

    def init_hidden(self, bs):
        return torch.zeros(1, bs, self.hidden_size)

# decoder = DecoderRNN(1, 30, 100, 10)
# h = decoder.init_hidden()
# a = torch.LongTensor([[1]])
# e = torch.randn(1, 10, 100)
# print(a.size())
# o, h = decoder(a, h, e)
# print(o)
# print(h)


